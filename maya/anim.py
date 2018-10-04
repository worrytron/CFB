# Built-in modules
import re
import os.path
import shutil

# Maya-specific modules
import pymel.core as pm

# Internal modules
from pipeline.maya import project


##############################################################################
# .atom files
##############################################################################
def atomPreFlight(*a):
    ''' Checks that the current selection and scene are valid for atom import/export '''
    # get selection
    try:
        sel = pm.ls(sl=True)[0]
    except IndexError:
        pm.warning('Export Atom  ERROR Select a RIG node!')
        return False
    # check that the scene is controlled by the pipeline
    try: scene_controller = pm.PyNode('sceneControlObject')
    except: 
        pm.warning('Export Atom  ERROR Scene not set up for the pipeline.  Cannot export .atom')
        return False
    # check that a rig node is selected
    if sel not in listAllRigNodes(): 
        pm.warning('Export Atom  ERROR Select a RIG node!')
        return False

    return sel


def exportAtom(*a):
    ''' Exports the entire hierarchy below the current selection as an .atom file '''    
    sel = atomPreFlight()
    if not sel:
        return

    msg = 'Add a custom tag to the filename?  i.e. \'LOGO\', \'CAM\', or whatev.'
    export_path = getAnimPath('atom', msg, 1)

    # select the whole heirarchy
    pm.select(hierarchy=True)

    # export the .atom for the selected heirarchy
    try:
        # Load the atom plugin
        pm.loadPlugin("atomImportExport.mll")
        # Export the selection
        pm.exportSelected(
            export_path, 
            type='atomExport'
            )
        pm.warning('Export Atom  SUCCESS')
    except RuntimeError:
        pm.warning('Export Atom  ERROR During export. (Most likely there\'s no animation to export.)')
        return
    
    # Restore original selection.
    pm.select(sel)


def importAtom(*a):
    ''' Imports an atom file into the hierarchy below the current selection '''
    sel = atomPreFlight()
    if not sel:
        return
    # select the whole hierarchy
    pm.select(hierarchy=True)

    atom_file = pm.fileDialog2(fm=1, dir=getAnimPath('atom', '', 1, folder_only=True))[0]
    
    if atom_file:
        pm.importFile(atom_file, defaultNamespace=True)
        return
    else:
        return


##############################################################################
# .abc files
##############################################################################
def exportAbc(*a):
    # get selection
    sel = pm.ls(sl=True)[0]
    # get frame range
    start = str(pm.playbackOptions(q=True, min=True))
    end   = str(pm.playbackOptions(q=True, max=True))

    msg = 'Add a custom tag to the filename?  i.e. \'LOGO\', \'CAM\', or whatever it is you\'re exporting.'
    export_path = getAnimPath('abc', msg, 0)

    pm.Mel.eval(
        "AbcExport -j \"-frameRange {0} {1} -worldSpace -uvWrite -dataFormat ogawa -root {2} -file {3}\";".format(
            start, end, sel, export_path.replace('\\','/')))
    pm.warning('Export Alembic  SUCCESS Wrote to {0}'.format(export_path))
    return


##############################################################################
# camera & playblasting
##############################################################################
def bakeCamera( cam, exp=False, *args, **kwargs ):
    """Duplicates a baked version of a camera.  Expects a valid camera transform node."""
    # Frame range
    frame_range = ( 
        pm.playbackOptions( q=True, min=True ), 
        pm.playbackOptions( q=True, max=True )
        )
    
    # Duplicate the camera
    dup_cam = pm.duplicate( cam, name=(cam.name() + '_Baked') )[0]
    
    # Parent new camera to world.
    try: pm.parent(dup_cam, w=True)
    except RuntimeError: pass
    
    # Constrain new camera to old
    const = pm.parentConstraint( cam, dup_cam, mo=True )
    
    # Bake it
    pm.bakeResults( dup_cam, t=frame_range )

    # Delete the constraint
    pm.delete(const)

    return dup_cam


def exportCamera(*a):
    # get selection
    sel = pm.ls(sl=True)[0]

    # find the first camera
    children = sel.getChildren()
    for child in children:
        if type(child) is not pm.nodetypes.Camera:
            continue
        else:
            break

    # bake it
    camera = bakeCamera(child)
    
    # get the scene export path
    export_path = getAnimPath('fbx', '', 0, override_name='cam')

    # select and export camera
    pm.select(camera)
    pm.exportSelected(export_path, type='Fbx')
    pm.warning('Successfully exported camera  {0}  to  {1}.'.format(camera, export_path))
    return True


def importCamera(*a):
    cam_path = getAnimPath('Fbx', '', 0, 1, override_name='cam')

    fbx_file = pm.fileDialog2(fm=1, dir=cam_path)[0]
    
    if fbx_file:
        pm.importFile(fbx_file, defaultNamespace=True)
        return
    else:
        return


def playblast(*a):

    def __incrVersion(backup_path, version, name):
        backup_name = name + '_' + str(int(version)).zfill(4) + '.mov'
        if os.path.exists(os.path.join(backup_path, backup_name)):
            version += 1
            backup_name = __incrVersion(backup_path, version, name)
        return backup_name
    
    # Frame range
    frame_range = ( 
        pm.playbackOptions( q=True, min=True ), 
        pm.playbackOptions( q=True, max=True )
        )

    file_name, project_path = project.getProject()
    
    # v:\DELIVERABLE\qt\DELIVERABLE_ANIM.mov
    qt_folder = os.path.join(project_path, 'qt')
    backup_folder = os.path.join(qt_folder, 'backup')

    output_path = os.path.join(qt_folder, file_name+'.mov')
    
    if os.path.exists(output_path):
        backup_path = __incrVersion(backup_folder, 1, file_name) 
        #print os.path.join(backup_folder, backup_path)
        os.rename(output_path, os.path.join(backup_folder, backup_path))


    pm.Mel.eval('setCurrentFrameVisibility(1);')
    pm.playblast(
        startTime      = frame_range[0],
        endTime        = frame_range[1],
        filename       = output_path,
        forceOverwrite = True,
        format         = 'qt',
        compression    = 'H.264',
        orn            = False,
        width          = 960,
        height         = 540,
        percent        = 100,
        quality        = 70,
        clearCache     = True
        )


##############################################################################
# helper functions
##############################################################################
def getAnimPath(filetype, message, use_maya_subfolder, folder_only=False, override_name=False):

    # check that the scene is controlled by the pipeline
    try: scene_controller = pm.PyNode('sceneControlObject')
    except: pass

    if override_name:
        folder_name = override_name
    else:
        folder_name = filetype

    # set up export paths
    scene       = project.Scene()
    # The use_maya_subfolder flag determines whether this export goes into a folder
    # below the main project folder or below the maya folder instead.
    anim_folder = {0: scene.project_folder, 1: scene.maya_project_folder}[use_maya_subfolder] + '\\{0}\\'.format(folder_name)
    anim_file   = scene.scene_name

    # If exporting (i.e. determining a full destination file name)
    if not folder_only:
        if override_name:
            anim_file += '.{0}'.format(override_name)

        else:
            custom_string = pm.promptDialog(
                title='Custom name tag?',
                message=message,
                text='',
                b=['OK', 'No'],
                db='OK',
                cb='No',
                ds='No'
                )
            if custom_string == 'OK':
                custom_string = pm.promptDialog(q=True, text=True)
            else:
                custom_string = ''
            anim_file += '_{}.{}'.format(custom_string, filetype)

        return anim_folder + anim_file

    # i.e., if import (just returning a path)
    elif folder_only:
        return anim_folder


def listAllRigNodes(*a):
    comp = re.compile('.:RIG$')
    return pm.ls(regex=comp)
