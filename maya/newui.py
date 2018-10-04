import pymel.core as pm
from pipeline.database.team import Team
from pipeline.maya import project


### UI
class SceneBuilder(pm.uitypes.Window):

    def __init__(self):

        self.tricode_list = []
        self._scene_type = {1: 'Team Logo Update',
                            2: 'Blue City Weekly',
                            3: 'New Years\' Six Elements',
                            4: 'Playoff Elements',
                            5: 'Current Scene Only'}

        # WINDOW UI SHIT
        self.wh = (500,500)
        self.setTitle('CFB Versioning Tool')
        self.setResizeToFitChildren(1)
        
        main = pm.formLayout()

        ui_text_tricodes = pm.textFieldGrp(
            'ui_text_tricodes',
            l='Tricode List (comma-separated)',
            cw2=[200,200],
            cl2=['right','right'],
            p=main
            )

        ui_btn_go = pm.button(
            'ui_btn_go',
            l='B U I L D',
            c=self.btn_go,
            p=main)

        main.redistribute()

    # PRIVATE HELPER FUNCTIONS
    def __preFlight(self):
        # check that this is a pipeline-managed scene
        if project.isScene():
            pass
        else: return False

        # check that it's a skeleton scene
        name, folder = project.getProject()
        if 'SKELETON' in name:
            pass
        else: return False

        # check that all the specified tricodes match real teams
        if self.__getTricodes():
            pass
        else: return False

        return True


    def __getTricodes(self):
        # get user input from the UI
        tri_list = pm.textFieldGrp('ui_text_tricodes', q=True, text=True).replace(' ','').split(',')

        # check that all the user input is valid
        for tricode in tri_list:
            try: 
                team = Team(tricode)
            except AttributeError: 
                pm.warning('Scene Builder  ERROR Team {} not found in database.'.format(tricode))
                return None

        # push the update if the list is valid
        self.tricode_list = tri_list
        
        # success reported for preFlight()
        return True

    def btn_go(self, *a):
        self.__getTricodes()
        print self.tricode_list

