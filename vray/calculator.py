#####################################################################################
#####################################################################################
###                            V-Ray Samples Calculator                           ###
###                      Mark Rohrer - rastermancer@gmail.com                     ###
###             Latest version: http://www.github.com/worrytron/maya/             ###
###                                                                               ###
###                           Thanks to Toni Bratincevic                          ###
### http://www.interstation3d.com/tutorials/vray_dmc_sampler/demistyfing_dmc.html ###
###                           Tested with V-Ray 2.30.01                           ###
###                                                                               ###
#####################################################################################
#####################################################################################
import pymel.core as pm
import math


def run( *args, **kwargs ):
    """Use this function to run the calculator."""

    # Locking the DMC threshold
    rglobals = pm.PyNode('vraySettings')
    try: rglobals.dmcLockThreshold.set(1)
    except: pass
    
    #############################
    '''   MAYA INTERFACE      '''
    #############################

    try: pm.deleteUI( 'vraySampleCalcWin' )
    except: pass

    vraySampleCalcWin = pm.window( 'vraySampleCalcWin', title="V-Ray Sample Calculator", iconName='SAMP', s=False )
    winBox = pm.columnLayout()

    ################################
    ###   DMC SAMPLER SETTINGS   ###
    ################################

    frame = pm.frameLayout(l='Adaptive DMC Sampler Settings', w=416, fn='smallBoldLabelFont', cll=True, cl=False, p=winBox)
    subframe = pm.columnLayout( adjustableColumn=False, parent=frame )

    ################################
    ### PRIMARY RAYCAST SAMPLING ###
    ################################
    header = pm.text(l=' Primary raycast sampling', fn='smallBoldLabelFont', align='center', p=subframe)
    pm.separator(style='in', h=1, p=subframe)

    row = pm.rowLayout( parent=subframe, numberOfColumns=2, cw2=(370,20) )
    box = pm.columnLayout( parent=row, cw=370 )

    #
    min_subdivs_in = pm.intSliderGrp( 'min_subdivs_in',
                  field=True,
                  cw=(3, 140), 
                  label='DMC Min Subdivs', 
                  step=2, 
                  cc=__uiUpdate,
                  dc=__uiUpdate,
                  minValue=1, maxValue=64, 
                  fieldMinValue=1, fieldMaxValue=9999, 
                  value=1, 
                  ann='The number of initial eye rays cast per-pixel.', 
                  parent=box )
    #
    max_subdivs_in = pm.intSliderGrp( 'max_subdivs_in',
                  field=True,
                  cw=(3, 140),  
                  label='DMC Max Subdivs', 
                  step=2,
                  cc=__uiUpdate,
                  dc=__uiUpdate, 
                  minValue=1, maxValue=64, 
                  fieldMinValue=1, fieldMaxValue=9999, 
                  value=4, 
                  ann='The maximum number of eye rays that will be cast to average out\nlarge changes in value between sample returns. (See Threshold)', 
                  parent=box )
    #
    thresh_val_in = pm.floatSliderGrp( 'thresh_val_in', 
                    field=True,
                    cw=(3, 140),  
                    label='DMC Threshold',
                    pre=3, 
                    cc=__uiUpdate,
                    minValue=0.001, 
                    maxValue=0.020, 
                    fieldMinValue=0.001, 
                    fieldMaxValue=0.020, 
                    value=0.010, 
                    ann="When the current raycast changes the previous value of the pixel\nby less thanthis amount, no more primary rays will be cast.\nUsually kept between 0.005 and 0.010.", 
                    parent=box )
    #
    adapt_amt_in = pm.floatSliderGrp( 'adapt_amt_in', 
                    field=True,
                    cw=(3, 140),  
                    label='Adaptive Amount',
                    pre=3, 
                    cc=__uiUpdate,
                    dc=__uiUpdate,
                    minValue=0.001, 
                    maxValue=1, 
                    fieldMinValue=0.001, 
                    fieldMaxValue=1, 
                    value=1, 
                    ann="Weights the total number of adaptive secondary samples available per trace.\nLower values mean more samples will be cast before becoming adaptive.", 
                    parent=box )
    #
    adapt_min_in = pm.intSliderGrp( 'adapt_min_in',
                   field=True,
                   cw=(3, 140),  
                   label='Adaptive Min Samples', 
                   step=2, 
                   cc=__uiUpdate,
                   dc=__uiUpdate,
                   minValue=2, maxValue=64, 
                   fieldMinValue=2, fieldMaxValue=100, 
                   value=8,
                   ann='For any given secondary trace loop, this value is the minimum number\nof secondary rays that will be cast. These secondary rays will always\nbe deducted from your available adaptive rays. It is a VERY important setting,\nand changing it can have significant impact on render time and quality.\n\nNormal values are between 4 and 8.  The smallest value used should be 2,\nbut this will produce very noisy results.', 
                   parent=box )
    #

    ##########################################
    ### SCENE SAMPLES SET & IMPORT BUTTONS ###
    ##########################################
    butt_box = pm.gridLayout(numberOfColumns=2, cellWidthHeight=(20,120), parent=row)
    scene_samp_imp = pm.button( 'scene_samp_imp', l="<", c=__sceneToCalc, parent=butt_box)
    scene_samp_exec = pm.button( 'scene_samp_exec', l=">", c=__calcToScene, parent=butt_box)
    #

    ##################################
    ### SECONDARY RAYCAST SAMPLING ###
    ##################################
    pm.separator(style='in', h=20, p=subframe)
    header = pm.text(l=' Secondary raycast subdivs', fn='smallBoldLabelFont', align='center', p=subframe)
    pm.separator(style='in', h=5, p=subframe)
    
    box = pm.columnLayout( p=subframe)
    subdivs_mult_in = pm.floatFieldGrp( 'subdivs_mult_in',
                                    l="Samples Multiplier",
                                    ann="Multiplies all secondary subdiv settings by this amount. Use this during optimization\nto find a good overall number of secondary traces for your scene.", 
                                    cc=__uiUpdate,
                                    nf=1, v=(1,0,0,0), 
                                    el=" x", parent=box, 
                                    cw3=(140, 35, 10))
    

    
    row = pm.rowLayout( parent=subframe, numberOfColumns=3, cw3=(230,158,20) )
    box = pm.columnLayout( parent=row, cw=230 )

    subdivs_in = pm.intSliderGrp( 'subdivs_in',
                   field=True,
                   cw=(3, 140),  
                   label='Subdivs', 
                   step=2, 
                   cc=__uiUpdate,
                   dc=__uiUpdate,
                   minValue=1, maxValue=128, 
                   fieldMinValue=1, fieldMaxValue=1000, 
                   value=10, 
                   ann='The number of subdivs set in your secondary component, such as a glossy shader or area light.', 
                   parent=box )



    ####################
    ''' RESULTS PANE '''
    ####################

    frame = pm.frameLayout(l='Results', w=416, fn='smallBoldLabelFont', cll=True, cl=False, p=winBox)
    subframe = pm.columnLayout( adjustableColumn=False, parent=frame )

    pm.separator(style='in', h=1, p=subframe)
    header = pm.text(l=' Primary Samples                 Secondary Samples             # Adaptive Samples', fn='smallBoldLabelFont', align='center', p=subframe)
    pm.separator(style='in', h=5, p=subframe)

    result_box = pm.rowLayout( width=400, nc=3, parent=subframe, rat=([1,'top',0], [2,'top',0], [3,'top',0]) )

    ####################
    ### PRIMARY ########
    ####################
    cwidth = (30,90)
    col1 = pm.columnLayout( width=133, p=result_box )
    label = pm.text( l=' Per Pixel:', fn='smallPlainLabelFont', p=col1)
    min_primary_box = pm.intFieldGrp( 'min_primary_box', l='Min: ', nf=1, v=(1,0,0,0), e=False, p=col1, bgc=(0.27,0.27,0.27), cw2=cwidth )
    max_primary_box = pm.intFieldGrp( 'max_primary_box', l='Max: ', nf=1, v=(1,0,0,0), e=False, p=col1, bgc=(0.27,0.27,0.27), cw2=cwidth )

    ####################
    ### SECONDARY ######
    ####################
    col2 = pm.columnLayout( width=133, p=result_box )
    label = pm.text( l=' Per Pixel:', fn='smallPlainLabelFont', p=col2)
    min_secondary_box = pm.intFieldGrp( 'min_secondary_box', l='Min: ', nf=1, v=(1,0,0,0), e=False, p=col2, bgc=(0.27,0.27,0.27), cw2=cwidth )
    max_secondary_box = pm.intFieldGrp( 'max_secondary_box', l='Max: ', nf=1, v=(1,0,0,0), e=False, p=col2, bgc=(0.27,0.27,0.27), cw2=cwidth )
    pm.separator(style='in', h=3, p=col2)
    label = pm.text( l=' Per Trace Loop:', fn='smallPlainLabelFont', p=col2)
    min_secondary_pt_box = pm.intFieldGrp( 'min_secondary_pt_box', l='Min: ', nf=1, v=(1,0,0,0), e=False, p=col2, bgc=(0.27,0.27,0.27), cw2=cwidth )
    max_secondary_pt_box = pm.intFieldGrp( 'max_secondary_pt_box', l='Max: ', nf=1, v=(1,0,0,0), e=False, p=col2, bgc=(0.27,0.27,0.27), cw2=cwidth )

    ####################
    ### ADAPTIVE #######
    ####################
    col3 = pm.columnLayout( width=133, p=result_box )
    label = pm.text( l='Available Per Trace Loop:', fn='smallPlainLabelFont', p=col3)
    avail_secondary_box = pm.intFieldGrp( 'avail_secondary_box', l='Amt: ', nf=1, v=(1,0,0,0), e=False, p=col3, bgc=(0.27,0.27,0.27), cw2=cwidth )



    ###############################
    ''' V-RAY DMC PROCESS NOTES '''
    ###############################

    frame = pm.frameLayout(l='V-Ray DMC Trace Loop Reference', w=416, fn='smallBoldLabelFont', cll=True, cl=True, p=winBox)
    subframe = pm.columnLayout( adjustableColumn=False, parent=frame, cal='left' )

    pm.text(l='The Basics: ')
    pm.text(l='The key to optimizing the Adaptive DMC renderer is in understanding that different\ncombinations of values will produce the same number of secondary samples\nper primary trace loop of a given component.  Practically speaking, this means it is a\nbalance between firing just enough PRIMARY traces for clean AA, and\njust enough SECONDARY traces for smooth gloss, shadows, or blur. ')
    pm.text(l='')
    pm.text(l='The best procuedure for optimizing is to balance your PRIMARY traces until clean\nedge sampling is achieved, and then turning your subdivs up or down on each\ncomponent until you\'re satisfied with the amount of noise they produce.\nThis calculator is therefore a guide to understanding the relationship between\nprimary and secondary sampling.')
    pm.text(l='')
    pm.text(l='Adaptive Algorithm:')
    pm.text(l='')
    pm.text(l='1. Primary samples are fired into the scene through the pixel grid.  This represents\n     the start of a \'trace loop\'.  The number of samples per pixel is equal to the square\n     of the DMC Min Subdivs value.')
    pm.text(l='')
    pm.text(l='2. If geometry is struck and the primary trace determines that more samples\n     are needed for AA, more primary traces will be queued.')
    pm.text(l='')
    pm.text(l='3. If geometry is struck, the surface will be queried for secondary tracing needs.\n     This includes glossy materials, area light illumination, GI, camera blurs, etc.')
    pm.text(l='')
    pm.text(l='4. Subloops are called for all secondary tracing.  Each secondary component gets\n     its own loop.  The number of secondary traces automatically queued is the\n     \'min secondary samples per-trace\' value.  If the \'max secondary samples per-trace\'\n     value is hit before the treshhold is achieved, more PRIMARY traces will be queued.')
    pm.text(l='')
    pm.text(l='5. For any loop, if the \'max samples per-pixel\' limit is hit, or if the threshold\n     value is satisfied, no more loops are queued.  Primary values take precedence\n     over Secondary values in this case.')
    pm.text(l='')
    pm.text(l='')
    pm.text(l='Conditions for termination of tracing (priority order):')
    pm.text(l='- If the \'maximum primary samples per-pixel\' value is reached tracing will stop.')
    pm.text(l='- If the returned color value of a primary trace changes the final pixel value by less\n  than the DMC threshold amount, tracing will stop.')
    pm.text(l='- If the  \'max secondary samples per-pixel\' of a component is reached, tracing of\n  that particular component will stop.')
    pm.text(l='- If the returned color value of a component changes the component\'s contribution to\n  the pixel by less than the DMC threshold amount, tracing of that component will stop.')

    pm.showWindow( 'vraySampleCalcWin' )
    __uiUpdate()


def __calculate( ui, *args ):
    """calculates the number of samples per-pixel and per-trace of a particular
       combination of DMC Sampler settings and component secondary subdivs.
      
       ui 
         : a dictionary of the current UI settings. """
	
    # protecting from garbage input.  min cannot be more than max.
    if ui['dmc_min_subdivs'] > ui['dmc_max_subdivs']:
        pm.intSliderGrp( 'max_subdivs_in', e=True, v=ui['dmc_min_subdivs'] )
        __uiUpdate()


    # # CALCULATIONS
    # # FORMULAS FROM http://www.cggallery.com/tutorials/dmc_calculator/

    # converting max primary subdivs to samples
    max_primary_pp = ui['dmc_max_subdivs'] ** 2
    min_primary_pp = ui['dmc_min_subdivs'] ** 2

    ### max secondary samples per trace = ( secondary subdivs * samples multiplier / total max samples ) 
    max_samp_trace = math.ceil( ((ui['subdivs'] ** 2) * ui['subdivs_mult']) / max_primary_pp )
    #max secondary sample traces cannot be less than the adaptive minimum
    if max_samp_trace < ui['adaptive_min']:
        max_samp_trace = ui['adaptive_min']
    '''elif adaptive_amt < 1: Can't remember what this was for
        if max_samp_trace < 1:
            max_samp_trace = 1'''
    ### max secondary samples per pixel = (max secondary samples per trace * total max samples )
    max_samp_pixel = max_samp_trace * max_primary_pp


    ### min secondary samples per trace = ( max secondary samples per trace * non-adaptive weight component )
    min_samp_trace = math.ceil( max_samp_trace * (1 - ui['adaptive_amt']) )
    # if fully adaptive, use the adaptive minimum instead of the non-adaptive weight component
    if min_samp_trace < ui['adaptive_min']: 
        min_samp_trace = ui['adaptive_min']

    ### min secondary samples per pixel = (minimum samples per trace * minimum primary samples per pixel)
    min_samp_pixel = min_samp_trace * min_primary_pp


    ### adaptive samples available per trace
    adaptive_samp_trace = max_samp_trace - min_samp_trace

    results = {}
    results.setdefault('min_primary_pp', min_primary_pp)
    results.setdefault('max_primary_pp', max_primary_pp)
    results.setdefault('min_samp_pixel', min_samp_pixel)
    results.setdefault('max_samp_pixel', max_samp_pixel)
    results.setdefault('min_samp_trace', min_samp_trace)
    results.setdefault('max_samp_trace', max_samp_trace)
    results.setdefault('adaptive_samp_trace', adaptive_samp_trace)
    
    return results

    
def __uiGrok():
    """UI parser"""
    
    ui = {}
    ui['subdivs_mult'] = pm.floatFieldGrp( 'subdivs_mult_in', q=True, v=True )[0]
    #ui['mode_select'] = pm.radioButtonGrp( 'mode_sel_in', q=True, sl=True )
    ui['dmc_min_subdivs'] = pm.intSliderGrp( 'min_subdivs_in', q=True, v=True )
    ui['dmc_max_subdivs'] = pm.intSliderGrp( 'max_subdivs_in', q=True, v=True )
    ui['dmc_threshold'] = pm.floatSliderGrp( 'thresh_val_in', q=True, v=True )
    ui['adaptive_amt'] = pm.floatSliderGrp( 'adapt_amt_in', q=True, v=True )
    ui['adaptive_min'] = pm.intSliderGrp( 'adapt_min_in', q=True, v=True )
    ui['subdivs'] = pm.intSliderGrp( 'subdivs_in', q=True, v=True )
    
    return ui

    
def __uiUpdate( *args ):
    """ UI refresher """

    ui = __uiGrok()

    results = __calculate( __uiGrok() )

    pm.intFieldGrp( 'min_primary_box', edit=True, v=(results['min_primary_pp'], 0,0,0) )
    pm.intFieldGrp( 'max_primary_box', edit=True, v=(results['max_primary_pp'], 0,0,0) )

    pm.intFieldGrp( 'min_secondary_box', edit=True, v=(results['min_samp_pixel'], 0,0,0) )
    pm.intFieldGrp( 'max_secondary_box', edit=True, v=(results['max_samp_pixel'], 0,0,0) )
	
    pm.intFieldGrp( 'min_secondary_pt_box', edit=True, v=(results['min_samp_trace'], 0,0,0) )
    pm.intFieldGrp( 'max_secondary_pt_box', edit=True, v=(results['max_samp_trace'], 0,0,0) )

    pm.intFieldGrp( 'avail_secondary_box', edit=True, v=(results['adaptive_samp_trace'], 0,0,0) )
	
    ''' Still not sure about this whole adaptive min samples thing....
    if results[7] < 1:
        pm.intSliderGrp( 'adapt_min_in', edit=True, en=False )
    elif results[7] == 1:
        pm.intSliderGrp( 'adapt_min_in', edit=True, en=True )
    '''

    
def __sceneToCalc( *args ):
    """ Copies the DMC-related V-Ray globals settings to the calculator UI."""
    
    # V-ray globals
    globals = pm.PyNode('vraySettings')
    # V-ray scene settings to dictionary
    settings = {'dmc_min_subdiv': globals.dmcMinSubdivs.get(),
                'dmc_max_subdiv': globals.dmcMaxSubdivs.get(),
                'dmc_threshold': globals.dmcs_adaptiveThreshold.get(),
                'adaptive_min': globals.dmcs_adaptiveMinSamples.get(),
                'adaptive_amt': globals.dmcs_adaptiveAmount.get(),
                'subdivs_mult': globals.dmcs_subdivsMult.get()}
    
    # Transfer scene settings to UI
    pm.intSliderGrp('min_subdivs_in', e=True, v=settings['dmc_min_subdiv'])
    pm.intSliderGrp('max_subdivs_in', e=True, v=settings['dmc_max_subdiv'])
    pm.floatSliderGrp('thresh_val_in', e=True, v=settings['dmc_threshold'])
    pm.intSliderGrp('adapt_min_in', e=True, v=settings['adaptive_min'])
    pm.floatSliderGrp('adapt_amt_in', e=True, v=settings['adaptive_amt'])
    pm.floatFieldGrp('subdivs_mult_in', e=True, v=(settings['subdivs_mult'], 0,0,0))
    
    # .. and refresh
    __uiUpdate()
    
    return True


def __calcToScene( *args ):
    """ Sets the active scene DMC settings to what's currently in the calculator """

    # Get the V-Ray settings node.
    rglobals = pm.PyNode('vraySettings')
    # Get the current calculator settings from the UI.
    settings = __uiGrok()
    
    # Set values
    rglobals.dmcMinSubdivs.set( settings['dmc_min_subdivs'] )
    rglobals.dmcMaxSubdivs.set( settings['dmc_max_subdivs'] )
    rglobals.dmcs_adaptiveThreshold.set( settings['dmc_threshold'])
    rglobals.dmcs_adaptiveMinSamples.set( settings['adaptive_min'])
    rglobals.dmcs_adaptiveAmount.set( settings['adaptive_amt'])
    rglobals.dmcs_subdivsMult.set( settings['subdivs_mult'])
    
    return True

