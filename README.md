Maya/Nuke/V-Ray Pipeline
Intended for private / collaborative use only.  It's fine if you borrow, just 
toss a link to my github page in your comments.

INSTALLATION
- Install YAML libraries for mayapy and nuke python:
  http://pyyaml.org/ - Tested & developed using PyYAML 3.11

- Pull this repository and the 'cg' repository into your desired folder
  and run the following commands.  (To setup all users in your team,
  you can add these commands to userSetup.py in an evalDeferred()
  function):

    import sys
    sys.path.append('your root installation path')

    import cg
    import pipeline
    pipeline.cfb_ui.run() # not implemented yet

------------------------------------------------------------------------------

QUICK TUTORIALS

These tutorials are intended for power users, to understand the function and
organization of the pipeline's modules.

- To initialize a set of project definitions (folders, global variables, etc..)

        import pipeline.cfb as cfb
        # Note that the project definition module is necessary to initialize any
        # function relying on a specific project folder structure or set of global
        # variables.

- The SceneManager object controls the project folder structure on the network,
  the Maya project definition (workspace.mel), and manages scene saving, opening,
  backup duties within Maya.  This command initializes the project if necessary,
  otherwise it ensures that the user isn't overwriting anything that already exists
  and sets its maya project accordingly.

        scene = pipeline.maya.SceneManager(cfb.ANIM_BASE_DIR, cfb.FOLDER_STRUCTURE)
        # If this command is run on a pipeline-managed scene, it simply re-initializes
        # itself based on values stored in scene's sceneControlObject node (a locator.)

- To save / rename a scene:

        scene.save() 
        # overwrites the master scene file and increments the backup
        scene.rename() 
        # also saves the scene
        scene.open()
        # If the scene opened is already pipeline-managed, it simply sets the maya
        # project correctly.  Otherwise it attempts to initialize the scene.


- To sort a scene / set it up for rendering:

        sort = pipeline.maya.sort.SortControl(cfb.SORTING_DATABASE, 'NAME_OF_ELEMENT', cfb.FRAMEBUFFERS)
        # This object needs to be initialized for every asset in the scene to be
        # sorted.  The sorting.yaml database 'ELEMENT' attribute is currently the
        # only list of supported element/asset types.  

        sort.run() 
        # This command makes the render layers, enables the framebuffers and sorts 
        # objects into the correct layers with the correct visibility flags.


- To make a new asset / export an asset
        
        pipeline.maya.asset.makeNew()
        pipeline.maya.asset.sanityCheck()
        pipeline.maya.asset.export() 
        # Export overwrites the existing version of the asset and makes a backup. 
        # Includes sanity checks

- To reference an asset in:

        pipeline.maya.ui.referenceSelector() 
        # This opens a UI which forces the user to select a valid project namespace.

UPCOMING FEATURES
- Maya UI widget            (maya/ui.py)
- Scene opening & init      (maya/project.py)
- Scene sorting on the fly  (maya/sort.py)
- Scene sorting by database (maya/sort.py)
- Factory scene creation    (maya/factory.py)
- Equivalent versions for all necessary functionality in Nuke

------------------------------------------------------------------------------
##############################################################################
CHANGELOG
##############################################################################
------------------------------------------------------------------------------
02/07/15

- The following modules are working and tested -- all command line at the moment
    - Sort controller       (maya/sort.py)
    - Project creation      (maya/project.py)
    - Scene saving & backup (maya/project.py) (open() currently doesn't work)
    - V-Ray framebuffers    (vray/renderElements.py)
    - V-Ray mattes          (vray/mattes.py) - note this is my OLD version
    - V-Ray set management  (vray/utils.py)
    - Teams database        (database/team.py)


- The following modules are due to be deprecated, once their useful code is
  copied into the correct modules & tested.
    - Old team module       (maya/team.py)
    - Build module          (maya/build.py)
    - Switch Team module    (maya/switchTeam.py) <-- this will be archived for
      championship purposes only

