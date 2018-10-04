# Built-in modules
import os

# Maya-specific modules
import maya.cmds as cmds
import pymel.core as pm
import pymel.core.system as pmsys

# Internal modules
from pipeline import cfb


def isScene(*a):
    try:
        test = pm.PyNode('sceneControlObject')
        return True
    except pm.MayaNodeError:
        pm.warning('Scene Setup  ERROR This is not a pipeline-managed scene.  Please run Scene Setup.')
        return False


def getProject(*a):
    if not isScene():
        return

    scene = Scene()

    return (scene.scene_name, scene.project_folder)


class Scene(object):
    def __init__(self, delay=False):
        # The base path for all projects
        self.base_path = cfb.ANIMATION_PROJECT_DIR
        # Dictionary for this project's folder structure.  Found in pipeline.<project_name> module.
        self.folder_structure = cfb.FOLDER_STRUCTURE

        # The name of the project.  
        # Ex: "CFB_S_REJOIN_01"
        self.project_name = ''
        # The name of the scene (including variation).  This is what scene files, render folders, etc will be named.  
        # Ex: "CFB_S_REJOIN_01_GAMEDAY"
        self.scene_name = ''

        # The project folders of the scene file.  
        # Ex: "V:\CFB_S_REJOIN_01\"
        self.project_folder = ''
        # Ex: "V:\CFB_S_REJOIN_01\maya\"
        self.maya_project_folder = ''
        # Ex: "V:\CFB_S_REJOIN_01\maya\backup\"
        self.backup_folder = ''

        # The full paths relating to the scene file.
        # Ex: "V:\CFB_S_REJOIN_01\maya\scenes\CFB_S_REJOIN_01_GAMEDAY.mb"
        self.full_path = ''
        # The full path of the next queued backup of this scene file.
        # Ex: "V:\CFB_S_REJOIN_01\maya\backup\CFB_S_REJOIN_01_GAMEDAY_0002.mb"
        self.backup_path = ''

        # Strict is the property defining whether the scene is a strictly-controlled pipeline scene.
        # Strictly-controlled scenes must pass more stringent sanity checks before initializing or saving.
        self.strict = False

        if not delay:
            self._initScene()
            self.setProject()


    def __repr__(self, *a):
        print '\n'
        print 'Scene Information'
        print 'Project Name:   ' + self.project_name
        print 'Scene Name :    ' + self.scene_name
        print 'Project Folder: ' + self.maya_project_folder
        print 'Full Path :     ' + self.full_path
        print 'Next Backup     ' + self.backup_path
        print '\n'
        return ' '


    ##########################################################################
    # Checks & Initialization
    ##########################################################################
    def _checkStatus(self, *a):
        ''' Checks the status of the scene.  If the scene has a maya sceneControlObject, it pulls
            in scene data and returns true.  Otherwise, returns False.  Typically, an init would
            be run subsequent to this function, although it is safe to run at any time.  '''
        
        if not isScene():
            return False

        else:
            self._updateIn()
            return True


    def _isProject(self):
        ''' Checks whether a passed path/folder exists and has a maya project definition (workspace.mel). 
            Returns: Tuple ((0, 0): Doesn't exist, 
                            (1, 0): Folder exists but no variations (files) exist,
                            (1, 1): Folder and scene already exist .. prompt for a new name / overwrite '''
        folder_exists = os.path.exists(self.project_folder)
        scene_exists = os.path.exists(self.full_path)

        # If the project folder doesnt exist, just escape out immediately
        if not folder_exists:
            return (False, None)

        elif folder_exists and not scene_exists:
            return (True, None)

        elif scene_exists:
            return (True, True)


    def _initScene(self, *a):
        ''' If this is a new scene, organize it into a project.
            If this is a pre-existing scene not yet conformed to the project structure, 
            it will attempt to reconcile it. '''

        if self._checkStatus():
            return

        self.version = 1.0

        # CREATE SCENE CONTROLLER OBJECT.  This will store information about the scene
        # to simplify parsing when opening/saving the scene in the future.
        self.scene_controller = pm.createNode('locator', name='sceneControlObjectShape')
        pm.lockNode(self.scene_controller, lock=False)
        # Add custom attributes
        self.scene_controller.addAttr('ProjectName', dt='string')
        self.scene_controller.addAttr('SceneName', dt='string')
        self.scene_controller.addAttr('CustomTag', dt='string')
        self.scene_controller.addAttr('Version', at='float')
        self.scene_controller.addAttr('Strict', at='bool')
          # Set initialized custom attributes
        self.scene_controller.attr('Version').set(self.version)
        # Lock the node
        pm.lockNode(self.scene_controller, lock=True)
        

        # NAME PROMPT
        # Prompt for a project name
        name_query = pm.promptDialog(
            title='New Project Name',
            message='What project folder should this go in? i.e. \'CFB_S_REJOIN_01\'\nNote: Do not include \'_GAMEDAY\' or any other descriptors in this step.',
            text='CFB_',
            b=['OK', 'Cancel'],
            db='OK',
            cb='Cancel',
            ds='Cancel'
            )
        # Abort on cancel
        if name_query == 'Cancel':
            return False
        # Populate the value
        else: 
            self.project_name = pm.promptDialog(q=True, text=True)

        # Prompt for a custom tag for the scene        
        custom_string = pm.promptDialog(
            title='Custom name tag?',
            message='Do you want to create a custom descriptor for the scene file?  i.e. \'GAMEDAY\', \'PRIMETIME\', etc.',
            text='',
            b=['OK', 'No'],
            db='OK',
            cb='No',
            ds='No'
            )
        if custom_string == 'OK':
            self.custom_string = pm.promptDialog(q=True, text=True)
        else:
            self.custom_string = ''


        # INITIALIZATION TREE:
        # Name the scene and begin init process
        print '\nCREATING SCENE ... ' + self.scene_name 
        self._nameScene()
        
        # Set initialized values on the sceneController and generate full file paths
        print '\nUpdating scene controller ...'
        self._pushPull()

        # Check if the project exists, and if any scene files exist (and if so, get the next available variant)
        project_exists, scene_exists = self._isProject()

        # Either nothing exists, we make everything, save the scene, and we're done
        if not project_exists:
            try:
                print self.project_folder
                print '\nMaking folders ...'
                self.makeFolders()
                print '\nMaking project workspace ...'
                self.makeProject()
                print '\nSetting maya project ...'
                self.setProject()
                print '\nSaving file ...'
                self.save()
                print '\n... Done!'
                return True
            except: return False

        # Or: The project exists but this variant hasn't been saved yet, so just save, and we're done.
        elif project_exists and not scene_exists:
            try:
                self.makeFolders()
                self.setProject()
                self.save()
                return True
            except: return False

        # Or: Even the variant already exists, so we have a decision tree for the user.
        elif scene_exists:
            query = pm.confirmDialog(
                title='New Version?',
                message='There is already a file called ' + self.scene_name + '.mb. Select an option below.',
                b=['''Backup + Overwrite''', 'New Version', 'Cancel'],
                db='New Variant',
                cb='Cancel',
                ds='Cancel'
                )
            # 3A
            # Overwrite means we confirm it and just save without incrementing anything
            if query == '''Backup + Overwrite''':
                confirm = pm.confirmDialog(
                    title='Are you sure?',
                    message='Are you sure you want to overwrite this scene? DO NOT choose this option if things have already been rendered, unless you know what you\'re doing',
                    b=['Yes', 'No'],
                    db='Yes',
                    cb='Cancel',
                    ds='Cancel'
                    )
                if confirm:
                    self.save()
            # 3B
            # New variant means we need to increment the variable and save the scene
            elif query == 'New Version':
                self._rename()
                self.setProject()
                self.save()

            # Cleanup on abort
            else:
                try: pm.delete(self.scene_controller)
                except: pass
                return False

        else:
            try: pm.delete(self.scene_controller)
            except: pass
            return False


    ##########################################################################
    # Creators
    ##########################################################################
    def makeProject(self):
        ''' Make a new workspace definition file (workspace.mel) for this scene, if needed. '''
        # First, check that it doesn't already exist
        if os.path.exists(self.maya_project_folder + '\\workspace.mel'):
            #print 'Loaded workspace.mel from ' + self.base_path + '\\maya\\'
            return True
        # open the default workspace template
        with open(cfb.DEFAULT_WORKSPACE_MEL, 'r') as workspace:
            workspace_lines = workspace.readlines()
        # modify the line for render output
        workspace_lines[56] = "workspace -fr \"images\" \"" + self.project_folder.replace('\\','/') + "/render_3d\";\n"
        # and save it to the new project folder
        with open(self.maya_project_folder + 'workspace.mel', 'w') as workspace:
            workspace.writelines(workspace_lines)
        print 'Created workspace.mel for ' + self.maya_project_folder
        return True


    def makeFolders(self):
        ''' Make the folder template for a deliverable (meta-project -- including nuke, ae, etc).
            Note: this should probably be moved in later versions.'''
        main_folder = self.base_path + self.project_name
        if not os.path.exists(main_folder):
            os.mkdir(main_folder)

        for k,v in self.folder_structure.iteritems():
            this_folder = main_folder +"\\"+ k +"\\"
            print this_folder
            if not os.path.exists(this_folder):
                os.mkdir(this_folder) 
            if v != []:
                for _v in v:
                    sub_folder = this_folder + _v
                    print sub_folder
                    os.mkdir(sub_folder)
        return True


    ##########################################################################
    # Public setters
    ##########################################################################
    def setProject(self, *a):
        ''' Sets the current workspace to the controlled scene's project path.'''
        try:
            pmsys.Workspace.open(self.maya_project_folder)
            print 'Set project to: ' + self.maya_project_folder
            return True
        except:
            pm.warning('Failed to set the specified project. It probably doesn\'t exist')
            return False

    def rename(self, name=None, save=True):
        x = isScene()
        if not (x):
            return

        if not (name):
            prompt = pm.promptDialog(
                        title='Rename Scene',
                        message='Enter new descriptor tag (i.e. PRIMETIME)',
                        text='',
                        button=['OK','Cancel'],
                        db='OK',
                        cb='Cancel',
                        ds='Cancel'
                        )

            if prompt == 'OK':
                self.custom_string = pm.promptDialog(q=True, text=True)
            else: return

        elif (name):
            self.custom_string = name

        else: return

        self._nameScene()
        self.version = 1.0
        self._pushPull()
        
        if save and os.path.exists(self.project_folder) and os.path.exists(self.maya_project_folder):
            self.save()
            return
        else:
            if save:
                pm.warning('SAVE SCENE  ERROR One or more destination folders does not exist.')
                return
            else:
                return


    ##########################################################################
    # File system operations
    ##########################################################################
    def save(self, *a):
        ''' Saves a backup of the current scene and overwrites it as a master scene file. '''
        if not self.scene_controller:
            pm.warning('Save Scene  ERROR Can\'t use this command until you\'ve set up the scene in the pipeline.')

        # Save the backup
        self.backup_path = self._incrVersion()
        #if not os.path.exists(self.backup_path) or not\
        #        os.path.exists(self.maya_project_folder):     
        #    pm.warning('Save Scene  ERROR Could not find one or more destination folders.  Aborting save.')
        #    return   
        try:
            cmds.file(rename=self.backup_path)
            cmds.file(save=True, type='mayaBinary')
            pm.warning('Save Scene  SUCCESS Backup saved to {}'.format(self.backup_path))
        except:
            pm.warning('Save Scene  ERROR while saving backup. Save manually and check the script editor.')
        
        # Save the master
        try:
            cmds.file(rename=self.full_path)
            cmds.file(save=True, type='mayaBinary')
            pm.warning('Save Scene  SUCCESS New master saved to {}'.format(self.full_path))
        except:
            pm.warning('Save Scene  ERROR while saving new master. Save manually and check the script editor.')

    @classmethod
    def open(self, file_=None, force=False, *a):
        ''' Opens a scene browsing UI and sets the associated project.'''
        if not (file_):
            new_file = pm.fileDialog2(fm=1, ds=1, dir=cfb.ANIMATION_PROJECT_DIR)
            try: new_file = new_file[0]
            except: return
        else: new_file = file_

        try:
            pm.openFile(new_file, force=force)
        except RuntimeError:
            query = pm.confirmDialog(
                title='Save changes?',
                message='Your scene has unsaved changes. Save before closing?',
                button=['Yes','No','Cancel'],
                db='Yes',
                cb='Cancel',
                ds='Cancel'
                )
            if query == 'Yes':
                self.save()
                pm.openFile(new_file, force=force)
            elif query == 'No':
                pm.openFile(new_file, force=True)
            else: return False

        pm.evalDeferred("from pipeline.maya import project\nscene=project.Scene()")
        #pm.evalDeferred("scene = project.Scene()")


    ##########################################################################
    # Internal getters & setters (aka helper functions)
    ##########################################################################
    def _incrVersion(self, version_only=False):
        ''' This function recursively increments versions attempting to find the next available file name for a
            backup of the scene file. 

            Note that unlike _incrVariant(), this function will always change values in the SceneControl object,
            if it determines that the currently queued backup has already been saved.'''
        file_name = self.backup_folder + self.scene_name + '_' + self._formatVersion() + '.mb'

        if os.path.exists(file_name):
            self.version += 1
            file_name = self._incrVersion()
        
        if version_only:
            return self.version
        else:
            self.backup_path = file_name 
            return file_name

    def _formatVersion(self):
        return str(int(self.version)).zfill(4)
    
    def _nameScene(self):
        if self.custom_string != '':
            self.scene_name = self.project_name + '_' + self.custom_string
        else: 
            self.scene_name = self.project_name

    def _updateOut(self):
        ''' Updates the maya sceneControlObject with any internal changes made to the python SceneManager.'''
        # Set all the values to be stored on the sceneControlObject
        self.scene_controller.attr('Version').set(self.version)
        #self.scene_controller.attr('Variation').set(self.variant)
        self.scene_controller.attr('SceneName').set(self.scene_name)
        self.scene_controller.attr('ProjectName').set(self.project_name)
        self.scene_controller.attr('CustomTag').set(self.custom_string)
        self.scene_controller.attr('Strict').set(self.strict)

    def _updateIn(self):
        ''' Updates the python SceneControl object with any changes made to the sceneControlObject (such as 
            when a new scene is opened.) '''
        self.scene_controller = pm.PyNode('sceneControlObject')
        # Getting attrs from sceneControlObject
        self.scene_name    = self.scene_controller.attr('SceneName').get()
        self.project_name  = self.scene_controller.attr('ProjectName').get()
        self.version       = self.scene_controller.attr('Version').get()
        #self.variant       = self.scene_controller.attr('Variation').get()
        self.custom_string = self.scene_controller.attr('CustomTag').get()
        self.strict        = self.scene_controller.attr('Strict').get()
        # Combining project name and variant to create a scene name
        self._nameScene()

        # Setting new values (i.e. doing the business)
        self.project_folder      = self.base_path + self.project_name + '\\'
        self.maya_project_folder = self.project_folder + 'maya\\'
        self.backup_folder       = self.maya_project_folder + 'backup\\'
        self.full_path           = self.maya_project_folder + 'scenes\\' + self.scene_name + '.mb'
        self.backup_path         = self._incrVersion()
        return True

    def _pushPull(self):
        self._updateOut()
        self._updateIn()


