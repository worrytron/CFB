import pymel.core as pm


def samplerInfo(*a):
    ''' Helper function that creates a samplerInfo if one does not exist, or 
    returns the one already in the scene, since only one is ever needed. '''

    try:
        si = pm.PyNode('samplerInfo1')
        return si
    except pm.MayaNodeError:
        si = pm.createNode('samplerInfo')
        return si

def vrayDirt( samples, distance, spread, light_color=(1,1,1), dark_color=(0,0,0) ):
    ''' Helper function that creates a VRayDirt node .. mostly used in the AO framebuffer function. '''

    ao = pm.createNode('VRayDirt')

    ao.subdivs.set(samples)
    ao.radius.set(distance)
    ao.distribution.set(spread)

    ao.whiteColor.set(light_color)
    ao.blackColor.set(dark_color)

    return ao


#######################
### RENDER ELEMENTS ###
#######################
def makeExTex( name=None, inTex=None ):
    ''' Make an extraTex framebuffer.  Optional flags for naming (node and 
        channel) and for an incoming 3D color/vector attribute.'''
    
    pm.mel.eval('vrayAddRenderElement ExtraTexElement;')
    _fb = __getLast()
    _fb.vray_considerforaa_extratex.set(0)
    if inTex:
        inTex >> _fb.vray_texture_extratex
    if name:
        _fb.vray_name_extratex.set(name)
        _fb.vray_explicit_name_extratex.set(name)
        pm.rename(_fb, name)
    return _fb


def make1DTex( name, inTex_X=None, inTex_Y=None, inTex_Z=None, aa=False ):
    ''' Make an extraTex framebuffer.  Optional flags for naming (node and 
        channel) and for individually specified scalar map channels. '''
    
    pm.mel.eval('vrayAddRenderElement ExtraTexElement;')
    _fb = __getLast()
    _fb.vray_considerforaa_extratex.set(1)
    if inTex_X: inTex_X >> _fb.vray_texture_extratex.vray_texture_extratexR
    if inTex_Y: inTex_Y >> _fb.vray_texture_extratex.vray_texture_extratexG
    if inTex_Z: inTex_Z >> _fb.vray_texture_extratex.vray_texture_extratexB
    if name:
        _fb.vray_explicit_name_extratex.set(name)
        _fb.vray_name_extratex.set(name)
        pm.rename(_fb, name)
    return _fb


def makeUV( name=None ):
    ''' Make a UV framebuffer.  Is not anti-aliased by definition. '''

    # Create / get the samplerInfo node in the scene
    si = samplerInfo()
    # Connect the u/v coord attributes of the SI node to an extratex
    fb = make1DTex( name, si.uvCoord.uCoord, si.uvCoord.vCoord )
    # Disable AA
    fb.vray_considerforaa_extratex.set(0)
    fb.vray_filtering_extratex.set(0)
    
    return fb


def makeAO( name=None ):
    ''' Make an AO framebuffer. '''

    ao = vrayDirt( 32, 30, 1 )
    fb = makeExTex( name, ao.outColor )

    return fb


def makePPW( name=None ):
    ''' Make a pointWorld framebuffer.  It is not anti-alised by definition. '''

    # Create / get the samplerInfo node in the scene
    si = samplerInfo()
    # Connect the pointWorld attributes of the SI node to an extratex
    fb = makeExTex( name, si.pointWorld )
    # Disable AA
    fb.vray_considerforaa_extratex.set(0)
    fb.vray_filtering_extratex.set(0)
    
    return fb


def makeNormal( name=None ):
    '''Make a normals framebuffer. '''

    pm.Mel.eval('vrayAddRenderElement normalsChannel;')
    _fb = __getLast()
    #_fb.vray_filtering_bumpnormals.set(aa)
    
    if name:
        _fb.vray_name_normals.set(name)
        pm.rename(_fb, name)

    return _fb


def makeBumpNormal( name=None ):
    '''Make a bumped-normals framebuffer. '''

    pm.Mel.eval('vrayAddRenderElement bumpNormalsChannel;')
    _fb = __getLast()
    #_fb.vray_filtering_bumpnormals.set(aa)
    
    if name:
        _fb.vray_name_bumpnormals.set(name)
        pm.rename(_fb, name)

    return _fb


def makeZDepth( name=None, aa=False, minMax=(0,20) ):
    '''Make a depth framebuffer.  Optional flag controls anti-aliasing.'''

    pm.Mel.eval('vrayAddRenderElement zdepthChannel;')
    _fb = __getLast()

    if name:
        _fb.vray_name_zdepth.set(name)
        pm.rename(_fb, name)
    
    _fb.vray_filtering_zdepth.set(aa)

    _fb.vray_depthClamp.set(0)
    _fb.vray_depthBlack.set(minMax[0])
    _fb.vray_depthWhite.set(minMax[1])

    return _fb


def makeMVector( name=None, maxV=None ):
    ''' Make a motion vectors framebuffer.  Optional flag controls the initial 
        max displacement.'''

    pm.Mel.eval('vrayAddRenderElement velocityChannel')
    _fb = __getLast()
    _fb.vray_filtering_velocity.set(0)
    _fb.vray_clamp_velocity.set(0)
    _fb.vray_ignorez_velocity.set(0)

    if maxV:
        _fb.vray_max_velocity.set(maxV)
    if name:
        _fb.vray_filename_velocity.set(name)
        pm.rename(_fb, name)
    return _fb


def makeMultiMatte( name=None, r=None, g=None, b=None, mat=False ):
    ''' Make a multimatte framebuffer.  Optional flags including the mat_id 
        per channel, and a material id (as opposed to object id) flag.'''

    pm.Mel.eval('vrayAddRenderElement MultiMatteElement')
    _fb = __getLast()
    
    if name:
        _fb.vray_name_multimatte.set(name)
        pm.rename(_fb, name)
 
    try: _fb.vray_redid_multimatte.set(r)
    except: _fb.vray_redon_multimatte.set(0)

    try: _fb.vray_greenid_multimatte.set(g)
    except: _fb.vray_greenon_multimatte.set(0)

    try: _fb.vray_blueid_multimatte.set(b)
    except: _fb.vray_blueon_multimatte.set(0)

    _fb.vray_usematid_multimatte.set(mat)

    return _fb


def makeFresnel( name=None ):
    ''' Make a fresnel framebuffer. '''
    #si = samplerInfo()
    #fb = make1DTex('Fresnel', si.facingRatio, si.facingRatio, si.facingRatio)
    fresnel = pm.mel.eval('shadingNode -asTexture VRayFresnel;')
    fb = makeExTex('Fresnel', pm.PyNode(fresnel).outColor)
    return fb


def makeFacingRatio( name=None ):
    ''' Make a facing ratio framebuffer. '''
    si = samplerInfo()
    fb = make1DTex('facingRatio', si.facingRatio, si.facingRatio, si.facingRatio)
    return fb


def makeUserColor( name=None ):
    ''' Make a VRay User Color node. '''

    _uc = pm.PyNode( pm.mel.eval('shadingNode -asUtility VRayUserColor;') )
    if name:
        pm.rename(_uc, 'colorNode_' + name)
    _uc.color.set(0,0,0)
    _uc.userAttribute.set(name)
    return _uc


def makeLightComponentBuffer( name ):
    ''' Make a light component buffer (diffuse, reflection, etc).
        Valid keywords: diffuse
                        specular
                        reflection
                        refraction
                        selfIllum
                        GI
                        SSS
                        totalLight
                        shadow
                        lighting '''

    FB_MEL_COMMAND = {
        'reflection': 'vrayAddRenderElement reflectChannel;',
        'specular'  : 'vrayAddRenderElement specularChannel;',
        'diffuse'   : 'vrayAddRenderElement diffuseChannel;',
        'refraction': 'vrayAddRenderElement refractChannel;',
        'SSS'       : 'vrayAddRenderElement FastSSS2Channel;',
        'lighting'  : 'vrayAddRenderElement lightingChannel;',
        'GI'        : 'vrayAddRenderElement giChannel;',
        'selfIllum' : 'vrayAddRenderElement selfIllumChannel;',
        'shadow'    : 'vrayAddRenderElement shadowChannel;',
        'totalLight': 'vrayAddRenderElement totalLightChannel;',
    }
    

    try:
        exists = pm.PyNode(name)
        return exists
    except pm.MayaNodeError:
        pm.mel.eval( FB_MEL_COMMAND[name] )
        node = __getLast()
        pm.rename(node, name)
        return node 
    except:
        pm.warning('RENDER ELEMENTS :: Could not create a lighting component framebuffer: ' + name)


def makeUtilityBuffer( name ):
    ''' Using the AOV helper functions outlined above, create a utility framebuffer.
        Valid keywords: zDepth
                        normals
                        UV
                        AO
                        PPW
                        MV
                        fresnel
                        facingRatio
                        matte(A-Z) '''

    # Check that the node doesn't already exist.  This will also check that the node is actually
    # a framebuffer if a naming conflict is found.  If it's not a buffer, it just modifies the name.
    try:
        # Check if a node with that name already exists
        exists = pm.PyNode(name)
        
        # If so, is it a render element?  If so we can return out.
        if exists and (exists.nodeType() == 'VRayRenderElement'):
            return exists

        # Something else in the scene must have that name, so we hack.
        else: 
            pm.warning('Naming conflict found while creating framebuffer: ' + str(name))
            return False

    except:
        pass

    if name == 'zDepth':
        fb = makeZDepth( name )
        return fb

    elif name == 'normals':
        fb = makeNormal(name)
        return fb

    elif name == 'bumpNormals':
        fb = makeBumpNormal(name)
        return fb

    elif name == 'UV':
        fb = makeUV( name )
        return fb

    elif name == 'AO':
        fb = makeAO( name )
        return fb

    elif name == 'PPW':
        fb = makePPW( name )
        return fb

    elif name == 'MV':
        fb = makeMVector( name )
        return fb

    elif name == 'fresnel':
        fb = makeFresnel( name )
        return fb

    elif name == 'facingRatio':
        fb = makeFacingRatio( name )
        return fb

    elif 'matte' in name:
        uc = makeUserColor( name )
        fb = makeExTex( name, uc.outColor )
        return fb

def __getLast(): # stupid hacks.  (python does not return a string when using vray commands.)
    # Get all v-ray render elements
    _filter = pm.itemFilter(byType='VRayRenderElement')
    # From that list, reorder it by time created
    _list = pm.lsThroughFilter( _filter, sort='byTime', reverse=False)
    # Take just the most recent one
    _result = _list[len(_list)-1]

    return _result

