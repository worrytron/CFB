# Built-in modules
import maya.cmds as cmds
import os

# Maya-specific modules
import pymel.core as pm

# Internal modules
import cg.maya.rendering as rendering
import cg.maya.selection as select

from pipeline import cfb


def sanityCheck(report=True, model=False, shading=False, *a):
    """ Performs a simple check of an asset to see if it's ready for check-in.
        This includes checking for invalid members of the asset heirarchy and 
        valid metadata attributes (model-mode), as well as checking for bad 
        shading assignments (shading-mode)."""
    
    obj = select.single()
    if not obj:
        return False

    # Top node must be selected
    # Immediate failure if false
    if obj.getParent():
        pm.warning('Select top node of asset.')
        return False

    # Check for valid subgroups
    if model:
        sub_grps = obj.listRelatives()
        invalid_nodes = []
        for sg in sub_grps:
            if not ('GEO'  in str(sg) or 
                    'CAM'  in str(sg) or 
                    'LGT'  in str(sg) or
                    'RIG'  in str(sg) or
                    'LOCK' in str(sg)
                    ):
                invalid_nodes.append(sg)
        if len(invalid_nodes):
            pm.warning('Invalid groups found in asset: ' + str(invalid_nodes))
            return False
        pm.warning('Valid groups: pass')
        
        # Check the metadata for valid attributes
        try:
            attr_chk = pm.PyNode(obj).assetName.get()
            attr_chk = pm.PyNode(obj).assetPath.get()
            attr_chk = pm.PyNode(obj).assetVersion.get()
            del attr_chk
        except:
            pm.warning('Metadata not found.')
            return False

    if shading:
        # Check the shading of the object
        problem_shaders = rendering.generateShaderReport(squelch_valid=True)
        if len(problem_shaders):
            pm.warning('Mesh shading: fail')
            return False
        pm.warning('Mesh shading: pass')

    if report:
        pm.confirmDialog(title='Passed!',
                         message='Asset is ready for check-in.',
                         button=['OK']
                         )
    
    return True


def makeNew(*a):
    """ Makes an asset heirarchy for Maya, queries the user for a name, and 
    performs a bless()."""
    asset = pm.createNode('transform', name='ASSETNAME')
    geo = pm.createNode('transform', name='GEO', p=asset)
    repo = pm.createNode('transform', name='REPO', p=geo)
    rig = pm.createNode('transform', name='RIG', p=asset)
    attach = pm.createNode('transform', name='ATTACH', p=rig)
    cam = pm.createNode('transform', name='CAM', p=asset)
    swap = pm.createNode('transform', name='LGT', p=asset)
    lock = pm.createNode('transform', name='LOCK', p=asset)
    bless(asset)


def bless(obj=False):
    """ Creates and fills out an asset's custom metadata attributes.  
        Asset Path is determined on first export."""
    if not obj:
        obj = select.single()
        if not obj:
            return False
    # Create the attributes if necessary
    try:
        #if pm.addAttr(obj.assetName, q=True, exists=True):
        #    pass
        pm.PyNode(obj).attr('assetName')
    except:
        pm.addAttr(obj, ln='assetName', dt='string')
    try:
        #if pm.addAttr(obj.assetPath, q=True, exists=True):
        #    pass
        pm.PyNode(obj).attr('assetPath')
    except:
        pm.addAttr(obj, ln='assetPath', dt='string')
    try:
        #if pm.addAttr(obj.assetVersion, q=True, exists=True):
        #    pass
        pm.PyNode(obj).attr('assetVersion')
    except:
        pm.addAttr(obj, ln='assetVersion')        


    # Auto-fill values on first bless
    if obj.assetVersion.get() == 0.000:
        obj.assetVersion.set(1.000)
    if obj.assetName.get() == '' or obj.assetName.get() == None:
        query = pm.promptDialog(title='New Asset Name',
                                   message='Confirm name for asset >> ',
                                   text=str(obj),
                                   b=['OK', 'Cancel'],
                                   db='OK',
                                   cb='Cancel',
                                   ds='Cancel'
                                   )
        if query == 'OK':
            obj.assetName.set(pm.promptDialog(q=True, text=True))
            pm.rename(obj, obj.assetName.get())
        else:
            pm.delete(obj)
            return False

    # Fill out bless values
    name = obj.assetName.get()
    path = obj.assetPath.get()
    version = obj.assetVersion.get()

    # NOTE: path will return None on first run, by design
    return (name, version, path)


def export(*a):
    """ Parses an asset's custom attributes for information about the name and
        location of the asset in the filesystem.  Makes a backup of the asset 
        on export, if necessary."""
    # Backup logic
    def __incrVersion(backup_path, version, name):
        backup_name = name + '_' + str(int(version)).zfill(4) + '.mb'
        if os.path.exists(backup_path + backup_name):
            version += 1
            backup_name = __incrVersion(backup_path, version, name)
        return backup_name

    ## Selection manipulations
    # The goal here is to sort out the main asset node from any sort groups that are also selected.
    # The main asset then has to be passed down the chain for sanity checking, while the sort nodes
    # are stashed away for later use.
    
    sel = pm.ls(sl=True)
    xform_ct = 0
    sort_groups = []
    #print sel
    if len(sel) == 1:
        check = pm.confirmDialog(
            title='No sort sets?',
            message='No sort sets are selected. Export anyway?',
            button=['Yes','Cancel'],
            defaultButton='Yes',
            dismissString='Cancel')
        
        if check == 'Cancel':
            return False
        else: pass

    valid_node_list = [
        'VRayObjectProperties',
        'VRayRenderElementSet',
        'VRayLightMesh',
        'VRayDisplacement'
        ]
    
    # Check that only a single transform node and any number of valid nodetypes
    # are selected
    for obj in sel:
        if obj.nodeType() == 'transform' and xform_ct == 0:
            main_node = obj
            xform_ct = 1
            continue
        if obj.nodeType() == 'transform' and xform_ct == 1:
            pm.warning('More than one top-level transform selected.  Export cancelled.')
            return False
        if not obj.nodeType() in valid_node_list:
            pm.warning('Invalid top-level node selected.  Export cancelled.')
            return False
        
    # Bless object
    name, version, path = bless(main_node)
    
    # Assign an export path (if none)
    if path == None or path == '':
        path = pm.fileDialog2(fm=3, dir=cfb.MAIN_ASSET_DIR)[0]
        path += '\\' + name + '\\'
        main_node.assetPath.set(path)

    ### Backup & export
    # Build new file name
    export_name = path + name + '.mb'
    # If a file with that name already exists:
    if os.path.exists(export_name):
        ## Backup operation
        backup_path = path + 'backup\\'
        # Make the backup folder if it doesn't exist
        if not os.path.isdir(backup_path):
            os.mkdir(backup_path)

        # Increment the backup file version tag
        backup_name = backup_path + __incrVersion(backup_path, version, name)
        # & Copy the current asset into the backup folder, with the incremented file name
        os.rename(export_name, backup_name)
        pm.warning(
            'Successfully backed up asset to: ' + backup_name.replace('/','\\')
            )    
        # Update the asset in the scene with the current version
        main_node.assetVersion.set(main_node.assetVersion.get()+1)

    master_save = pm.exportSelected(
        export_name, 
        constructionHistory=True,
        channels=True,
        constraints=True,
        expressions=True,
        shader=True,
        preserveReferences=True,
        type='mayaBinary'
        )
    
    pm.warning('Successfully wrote asset to: ' + master_save.replace('/','\\'))


def importAsset( get_file=None, *a):
    """ Opens an import dialog starting at the CFB asset directory, 
        using no namespaces"""
    if not get_file:
        get_file = pm.fileDialog2(dir=cfb.MAIN_ASSET_DIR, ds=1, fm=1)
    
    if not get_file or get_file == '':
        return False
    
    in_file = pm.importFile(get_file, defaultNamespace=True)
    
    return in_file


def reference( file_to_ref, namespace, *a ):
    ''' A helper utility for maintaining clean and consistent namespacing when
        referencing.'''
    # Loop over all references to see if a reference is already loaded into 
    # the namespace
    ref = None

    for ref in pm.listReferences():
        if ref.namespace == namespace:
            break
        else: ref = None

    # If there's no reference loaded with that namespace, just delete it
    if not ref:
        try: pm.namespace(rm=namespace)
        except: pass
        ref = pm.createReference( file_to_ref, namespace=namespace )
        return ref

    # If there's already a reference loaded into that namespace, we have a decision for the user
    if ref:
        chk = pm.confirmDialog(
                title='Replace / create new reference?',
                message='There is already an existing reference in that namespace. Do you want to:\nSwap: Swap in the new asset (keep animation).\nRemove: Remove the old reference completely and start over.',
                b=['Swap','Remove','Cancel'],
                db='Swap',
                cb='Cancel',
                ds='Cancel'
                )
        if chk == 'Swap':
            ref.replaceWith( file_to_ref )
            return ref

        elif chk == 'Remove':
            ref.remove()
            ref = pm.createReference( file_to_ref, namespace=namespace )
            return ref


def namespaceSelector(get_file=False, *a):

    def _run(get_file):
        sel = pm.textScrollList('selectNamespace', q=True, si=True)[0]

        if not get_file:
            # Get target namespace & asset file from UI
            #get_file = pm.fileDialog2(dir=cfb.MAIN_ASSET_DIR, ds=1, fm=1)[0]
            assetSelector(init=True, mode='reference')

        else:
            reference(get_file, sel)

        try: 
            pm.deleteUI('refAsset')
            pm.deleteUI('sel_win')
        except: pass

    # UI for namespace selection
    try: pm.deleteUI('refAsset')
    except: pass

    widget = pm.window(
                'refAsset',
                title='Reference Asset into Namespace',
                tlb=True,
                rtf=True
                )
    main = pm.formLayout(p=widget)
    label = pm.text(label='What namespace will this reference into?')
    ns_box = pm.textScrollList(
                'selectNamespace', 
                numberOfRows=10, 
                parent=main,
                ams=False, 
                append=cfb.NAMESPACES
                )
    rf_but = pm.button(l='Reference into this Namespace', p=main, c=lambda *args: _run(get_file))
    main.redistribute(1,5,3)
    widget.show()


def assetSelector( init=None, mode='reference', *a):
    
    def _get( *a ):
        return pm.textScrollList( 'sel_box', q=True, selectItem=True )[0]
    

    def _run( mode, typ, *a ):
        if typ == 'generic':
            folder = cfb.MAIN_ASSET_DIR
        elif typ == 'team':
            folder = cfb.TEAMS_ASSET_DIR
        elif typ == 'template':
            folder = cfb.TEMPLATE_DIR

        asset_name = _get()
        
        if mode == 'reference':
            namespaceSelector(get_file = (folder + asset_name + "\\" + asset_name + ".mb"))
        elif mode == 'import':
            importAsset(get_file = (folder + asset_name + "\\" + asset_name + ".mb"))

    
    if init == True:    
        init = pm.confirmDialog( title='Select asset type:',
                                     message='What type of asset?',
                                     button=['Generic','Team','Cancel'],
                                     defaultButton='Generic',
                                     dismissString='Cancel'
                                     )

    if init == 'Cancel':
        return False    
    
    try:
        pm.deleteUI('select_win')
    except: pass
    
    select_win = pm.window( 'select_win',
                            title='Select asset:',
                            tlb=True, rtf=True, s=False,
                            width=150
                            )
    
    # Basic window layout
    top = pm.formLayout(p=select_win)
    sel_box = pm.textScrollList('sel_box', p=top, dcc=lambda *args: _run(mode,init.lower()))
    get_btn = pm.button('get_btn',
                        label='Select',
                        c=lambda *args: _run(mode, init.lower()),
                        h=25)
    top.redistribute(3.336,1)
    
    # Get the list of assets specified in init_win    
    asset_list = getAssetList(typ=init.lower())

    sel_list = pm.textScrollList( 'sel_box',
                                  e=True,
                                  append=asset_list,
                                  numberOfRows=min(25, max(10, len(asset_list)))
                                  )
   
    select_win.show()


def swapImportWithReference( obj=None, *a ):
    """ Deletes the selected asset from the scene and does the following:
        - References it back into the scene with a namespace
        - Removes any unused shaders from the scene
        
        It does not:
        - Explicitly remove other associated DAG nodes or sets from the scene"""
    
    confirm = pm.confirmDialog(title='You sure?',
                 message="""This script will delete the selected asset and its shading nodes,\nthen reference it back in.  Make sure the asset has exported\nsuccessfully and that you've saved your working file.""",
                 button=['OK','Cancel'],
                 defaultButton='OK',
                 dismissString='Cancel'
                 )
    if confirm == 'Cancel':
        return False
    
    if not obj:
        obj = select.single()
        if not obj:
            return False
    
    if sanityCheck(report=False, model=True):
        pass
    else: 
        pm.warning('Not a valid asset.  Cannot swap.')
        return False
    
    location = obj.assetPath.get()
    asset_name = obj.assetName.get()
    full_path = location + asset_name + ".mb"
    
    pm.delete(obj)
    
    try:
        pm.mel.eval('HypershadeWindow;hyperShadePanelMenuCommand("hyperShadePanel1", "deleteUnusedNodes");')
    except:
        pm.confirmDialog(title='Oops',
                         message="""Could not delete unused shading nodes.
You\'ll need to do it manually."""
                         )
    
    namespaceSelector(get_file=full_path)
    #return ref


def swapReferenceWithImport( obj=None, *a ):
    """ Based on the namespace of the current (referenced) selection, this 
        command does the following:
        - Removes the referenced scene completely
        - Imports the same scene into the default namespace """
    
    confirm = pm.confirmDialog(title='You sure?',
                 message="""This script will remove the selected reference
and its edits, then import it back in.  This cannot be undone so make sure
that you've saved your working file.""",
                 button=['OK','Cancel'],
                 defaultButton='OK',
                 dismissString='Cancel'
                 )
    if confirm == 'Cancel':
        return False
    
    if not obj:
        obj = select.single()
        if not obj:
            return False
    
    if not obj.nodeType() == 'transform':
        return False
    
    if not pm.referenceQuery(obj, rfn=True):
        pm.warning('Select a referenced asset!')
        return False
    
    asset_path = pm.referenceQuery(obj, f=True)
    
    try:
        ref_node = str(obj.split(':')[0]+'RN')
        cmds.file(removeReference=True, referenceNode=ref_node)
    except:
        pm.warning('Could not find RN node.  You may have to remove this one manually.')
        return False
    
    imp = pm.importFile(asset_path, defaultNamespace=True)
    
    return imp


def getAssetList( typ='generic' ):
    """ Return a list of all assets (folders) in various asset directories, 
        defined in 'typ' """
    if typ == 'generic':
        asset_list = os.listdir(cfb.MAIN_ASSET_DIR)
        asset_list = [a for a in asset_list if '000_FACTORY' not in a]
        asset_list.sort()
    
    elif typ == 'team':
        asset_list = os.listdir(cfb.TEAMS_ASSET_DIR)

    elif typ == 'template':
        asset_list = os.listdir(cfb.TEMPLATE_DIR)
    
    else:
        pm.warning('Invalid type passed to getAssetList()')

    asset_list[:] = [a for a in asset_list if '.' not in a]
    
    return sorted(asset_list)