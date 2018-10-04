# Pymel (Maya commands module)
import pymel.core as pm

# External modules
from pipeline.maya import asset
from pipeline.maya import sort
from pipeline.maya import build
from pipeline.maya import project
from pipeline.maya import anim
from pipeline.database import team

import pipeline.vray.utils as vrayutils
import pipeline.vray.vrayMatteTags as vmt

import yaml

# Other ESPN modules
import cg.maya.rendering as rendering
import cg.maya.selection as selection

# CFB global variables
import pipeline.cfb as cfb

reload(asset)
reload(sort)
reload(build)
reload(project)
reload(anim)
reload(team)
reload(vrayutils)
reload(rendering)
reload(selection)
reload(cfb)


blue = [0,0.38,0.52]
red  = [0.52,0,0]

######################################################################
# TRICODE LOOKUP
######################################################################

def lookupTricode(*a):
    
    def _lookup(*a):
        _team = team.Team(pm.textFieldGrp(text, q=True, text=True))
        
        try:
            _tri = _team.tricode
        except AttributeError:
            _tri = None
            
        if _tri:
            pm.text(tri, edit=True, label='         Tricode :  ' + str(_team.tricode))
            pm.colorSliderGrp( color_pri, edit=True, rgb=rendering.convertColor(_team.primary) )
            pm.colorSliderGrp( color_sec, edit=True, rgb=rendering.convertColor(_team.secondary) )
        else:
            pm.text(tri, edit=True, label='         Tricode :  NOT FOUND')
    
    try:
        pm.deleteUI('lookupTricode')
    except:
        pass
    
    win = pm.window('lookupTricode',
                    tlb=True, rtf=True, s=False,
                    title = 'Lookup Team Tricode'
                    )
    lay = pm.verticalLayout(width = 200, p=win)
    text = pm.textFieldGrp( label='Team Name : ', p=lay, cw2=(70,130), cc=_lookup)
    tri = pm.text(label='         Tricode : ', p=lay, align='left')
    color_pri = pm.colorSliderGrp( label='Primary : ', rgb=(0,0,0), cw3=(70,130,0) )
    color_sec = pm.colorSliderGrp( label='Secondary : ', rgb=(0,0,0), cw3=(70,130,0) )
    lay.redistribute()
    
    win.show()


######################################################################
# SORT CONTROL / TEAM SWITCHER
######################################################################

class SortControlLayout(pm.uitypes.Window):

    def __init__(self):

        self.wh = (220,500)
        self.setTitle('Scene Controller')
        #self.setToolbox()
        self.setResizeToFitChildren(1)
        self.setSizeable(1)
        self.setHeight(self.wh[1])
        #self.setWidth(self.wh[0])
        self.element_list = []

        with open(cfb.SORTING_DATABASE) as yaml_stream:
            self.stream = yaml.load_all(yaml_stream)
            for element in self.stream:
                self.element_list.append(element['ELEMENT'])

        main = pm.columnLayout()

        # TEAM SWITCHING LAYOUT
        top_frame = pm.frameLayout(
            l='Team Switcher',
            #w=self.wh[0], 
            fn='smallBoldLabelFont',
            cll=True,
            cl=False,
            p=main
            )
        
        column = pm.formLayout(p=top_frame)
        matchup_tgl = pm.radioButtonGrp(
            'matchup_toggle',
            label='',
            labelArray2=['Single Team', 'Matchup'],
            numberOfRadioButtons=2,
            cw=[(1,0)],
            cl2=['left','left'],
            cc=self.toggleMatchup,
            p=column
            )
        matchup_tgl.setSelect(1)

        home_team_txt = pm.textFieldGrp(
            'home_team_txt',
            l='Home Team',
            cw2=[78,130],
            cl2=['right','right'],
            p=column
            )
            
        away_team_txt = pm.textFieldGrp(
            'away_team_txt',
            l='Away Team',
            cw2=[78,130],
            cl2=['right','right'],
            en=False,
            p=column
            )

        diagnose_tgl = pm.checkBox('diagnose_tgl')
        diagnose_tgl.setLabel('Diagnose')
        diagnose_tgl.setValue(0)


        switchteam_btn = pm.button(
            'switch_team',
            l='L O A D   T E A M',
            bgc=red,
            c=self.loadBtn,
            p=column
            ) 
        
            
        column.redistribute()

        # SCENE SORTING LAYOUT
        bot_frame = pm.frameLayout(
            l='Scene Sorting',
            w=self.wh[0], 
            fn='smallBoldLabelFont', 
            cll=True, 
            cl=False, 
            p=main
            )

        # selection box
        column          = pm.formLayout(
                            p=bot_frame, 
                            #width=(self.wh[0]-5),
                            )
        pm.text(label='Select elements to sort', align='left', font='tinyBoldLabelFont', p=column)
        self.sel_box    = pm.textScrollList('sort_sel_box', p=column)
        pm.textScrollList('sort_sel_box',
            e=True,
            ams=True,
            append=self.element_list,
            numberOfRows=15,
            p=column
            )
                    
        # buttons
        self.sort_btn   = pm.button(l='SORT SCENE', bgc=blue, p=column, c=self.sortBtn)
        self.teardn_btn = pm.button(l='TEARDOWN SCENE', p=column, c=self.teardownBtn)
        
        box             = pm.formLayout(p=column)
        grid_l          = pm.gridLayout(nc=2,nr=2,cr=True, cwh=((self.wh[0]/2)-3, 15), p=box)
        self.open_btn   = pm.button(l='Open Scene', c=open_ui, p=grid_l)
        self.save_btn   = pm.button(l='Save Scene', c=save_ui, p=grid_l)
        self.rename_btn = pm.button(l='Rename Scene', c=rename_ui, p=grid_l)
        self.ref_btn    = pm.button(
                            l='Reference Editor', 
                            c=lambda *args: pm.mel.eval('ReferenceEditor;'), 
                            p=grid_l
                            )
        
        column.redistribute(1,15,3,1,4)
        #main.redistribute(1,4)


    def sortBtn(self, *a):
        sel = pm.textScrollList(
                'sort_sel_box',
                q=True,
                si=True
                )

        for s in sel:
            sc = sort.SortControl(s)
            sc.run()


    def loadBtn(self, *a):
        home_team = pm.textFieldGrp('home_team_txt', q=True, text=True)
        diag = pm.checkBox('diagnose_tgl', q=True, value=True)

        if home_team == '':
            pm.warning('Build Scene  ERROR Please enter a team name / tricode before proceeding.')

        if (pm.radioButtonGrp('matchup_toggle', q=True, sl=True)) == 1:
            build.loadTeamsStadium(home_team, diagnostic=diag)

        elif (pm.radioButtonGrp('matchup_toggle', q=True, sl=True)) == 2:
            away_team = pm.textFieldGrp('away_team_txt', q=True, text=True)
            build.loadTeamsStadium(home_team, away_team, diagnostic=diag)


    def teardownBtn(self, *a):
        sort.sceneTeardown()


    def toggleMatchup(self, *a):
        get_bool = pm.radioButtonGrp('matchup_toggle', q=True, sl=True)
        if get_bool == 1:
            pm.textFieldGrp('away_team_txt', e=True, enable=False)
        elif get_bool == 2:
            pm.textFieldGrp('away_team_txt', e=True, enable=True)
        else:
            pm.warning('SORT CONTROL  ERROR: Please select single-team or matchup.')
        return


def sortControlWidget(*a):
    s = SortControlLayout()
    
    if pm.dockControl('sortingDock', query=True, exists=True):
        pm.deleteUI('sortingDock')
    
    allowedAreas = ['right', 'left']

    dock = pm.dockControl( 
        'sortingDock', 
        floating=True, 
        label='Sorting / Team Switching', 
        area='left', 
        content=s, 
        allowedArea=allowedAreas
        )


######################################################################
# TRICODE LIST
######################################################################

def getTeamList(*a):
    
    prompt = pm.promptDialog(
        title = 'Enter List of Tricodes',
        message = 'Enter team tricodes, separated by commas >>',
        text = '',
        b=['OK', 'Cancel'],
        db='OK',
        cb='Cancel',
        ds='Cancel'
        )

    if prompt == 'OK':
        raw_list = pm.promptDialog(q=True, text=True)
        raw_list = raw_list.replace(" ", "")
        team_list = raw_list.split(',')
        print team_list
        return team_list

    else:
        return None


######################################################################
# PLAYOFF MATCHUP BUILDER
######################################################################

def playoffMatchupWin(*a):
    def run(*a):
        matchups = {'ROSE': (),
                    'SUGAR': (),
                    'ORANGE': (),
                    'COTTON': (),
                    'FIESTA': (),
                    'PEACH': ()
                    }

        matchups['ROSE'] = rose_bowl_grp.getText().replace(" ", "").split(',')
        matchups['ROSE'].append(rose_bowl_bool.getValue())

        matchups['SUGAR'] = sugar_bowl_grp.getText().replace(" ", "").split(',')
        matchups['SUGAR'].append(sugar_bowl_bool.getValue())        

        matchups['ORANGE'] = orange_bowl_grp.getText().replace(" ", "").split(',')
        matchups['ORANGE'].append(orange_bowl_bool.getValue())      

        matchups['COTTON'] = cotton_bowl_grp.getText().replace(" ", "").split(',')
        matchups['COTTON'].append(cotton_bowl_bool.getValue())      

        matchups['FIESTA'] = fiesta_bowl_grp.getText().replace(" ", "").split(',')
        matchups['FIESTA'].append(fiesta_bowl_bool.getValue())

        matchups['PEACH'] = peach_bowl_grp.getText().replace(" ", "").split(',')
        matchups['PEACH'].append(peach_bowl_bool.getValue())

        do_cgd = cgd_chk.getValue()
        do_nys = nys_chk.getValue()
        do_cfp = cfp_chk.getValue()

        build.nysOpensBuild(matchups, cgd=do_cgd, nys=do_nys, playoff=do_cfp)

    try:
        pm.deleteUI('matchup_win')
    except: pass

    matchup_win = pm.window('matchup_win',
                        tlb=True, rtf=0, s=1,
                        title='NYS / Playoff Matchup Selector'
                        )
    top = pm.verticalLayout(width = 200, p=matchup_win)

    lay = pm.horizontalLayout(p=top)
    inst_text = """    Enter the matchups for each bowl, separated by commas.
        Then check the boxes to the right to indicate the two PLAYOFF bowls."""
    inst_text_ui = pm.text(label=inst_text, font='boldLabelFont', align='left', p=lay)
    lay.redistribute()

    lay = pm.horizontalLayout(p=top)
    cgd_chk = pm.checkBox(l='Gameday', p=lay)
    nys_chk = pm.checkBox(l='NYS', p=lay)
    cfp_chk = pm.checkBox(l='Playoffs', p=lay)
    lay.redistribute()

    lay = pm.horizontalLayout(height = 10, p=top)
    rose_bowl_grp = pm.textFieldGrp(label='Rose Bowl:', p=lay, cw2=(70, 300))
    rose_bowl_bool = pm.checkBox(label='', p=lay)
    lay.redistribute(40,5)

    lay = pm.horizontalLayout(p=top)
    sugar_bowl_grp = pm.textFieldGrp(label='Sugar Bowl:', p=lay, cw2=(70, 300))
    sugar_bowl_bool = pm.checkBox(label='', p=lay)
    lay.redistribute(40,5)

    lay = pm.horizontalLayout(p=top)
    orange_bowl_grp = pm.textFieldGrp(label='Orange Bowl:', p=lay, cw2=(70, 300))
    orange_bowl_bool = pm.checkBox(label='', p=lay)
    lay.redistribute(40,5)

    lay = pm.horizontalLayout(p=top)
    cotton_bowl_grp = pm.textFieldGrp(label='Cotton Bowl:', p=lay, cw2=(70, 300))
    cotton_bowl_bool = pm.checkBox(label='', p=lay)
    lay.redistribute(40,5)

    lay = pm.horizontalLayout(p=top)
    fiesta_bowl_grp = pm.textFieldGrp(label='Fiesta Bowl:', p=lay, cw2=(70, 300))
    fiesta_bowl_bool = pm.checkBox(label='', p=lay)
    lay.redistribute(40,5)

    lay = pm.horizontalLayout(p=top)
    peach_bowl_grp = pm.textFieldGrp(label='Peach Bowl:', p=lay, cw2=(70, 300))
    peach_bowl_bool = pm.checkBox(label='', p=lay)
    lay.redistribute(40,5)

    lay = pm.horizontalLayout(p=top)
    exec_btn = pm.button(label='Build', height=30, align='right', c=run)
    lay.redistribute()

    top.redistribute(1)
    matchup_win.setHeight(200)
    matchup_win.setWidth(250)
    matchup_win.show()


######################################################################
# MAIN MENU 
######################################################################

def save_ui(*a):
    if project.isScene():
        scene = project.Scene()
        scene.save()
    else: 
        return

def open_ui(*a):
    project.Scene.open()
    #scene.open()

def rename_ui(*a):
    if project.isScene():
        scene = project.Scene()    
        scene.rename()
    else:
        return

def buildNys_ui(*a):
    team_list = getTeamList()

    if not team.checkTeams(team_list):
        return False

    build.nysBuild(team_list)

def buildPlayoff_ui(*a):
    team_list = getTeamList()

    if not team.checkTeams(team_list):
        return False

    build.playoffBuild(team_list)

def buildCity_ui(*a):
    team_list = getTeamList()

    if not team.checkTeams(team_list):
        return False

    build.cityWeeklyBuild(team_list)

def updateLogo_ui(*a):
    team_list = getTeamList()
    if team_list:
        for team in team_list:
            build.updateTeamLogo(team)

def init_scene(*a):
    scene = project.Scene()

try:
    pm.deleteUI('cfbTools')
except: pass
try:
    pm.deleteUI('pipeline')
except: pass

scene = project.Scene(delay=True)

g_main = pm.getMelGlobal('string','$gMainWindow')

pm.setParent(g_main)
mmenu = pm.menu('cfbTools', l='CFB \'15', to=True)

pm.setParent(menu=True)
#pm.menuItem(l="Reload Scripts", c=lambda *args: pm.evalDeferred( "exec('reload(cfb) in globals()')", lp=True )
#pm.menuItem(divider=True)
#pm.menuItem(l="Launch Widget", c=run)

#pm.menuItem(divider=True)

pm.menuItem(l="Open Scene", c=open_ui)
pm.menuItem(l="Save Scene", c=save_ui)
pm.menuItem(l="Rename Scene", c=rename_ui)

pm.menuItem(divider=True)
pm.menuItem(subMenu=True, to=True, l='General Utilities')
pm.menuItem(l="Select Meshes in Group", c=lambda *args: selection.shapes( pm.ls(sl=True), xf=True, do=True ))
pm.menuItem(l="Select Shader on Selected", c=lambda *args: rendering.getShader(select_result=True))
pm.menuItem(l="Make Offset Group", c=lambda *args: selection.createOffsetGrp( pm.ls(sl=True) ))
pm.menuItem(l="Lookup Tricode", c=lookupTricode)
pm.setParent(mmenu, menu=True)

pm.menuItem(divider=True)
#pm.menuItem(subMenu=True, to=True, label="Assets")
pm.menuItem(l="Build Factory Scene", c=lambda *args: build.factory())
pm.menuItem(l="Update Team Logo", c=updateLogo_ui)

#pm.menuItem(l="Sort Factory Scene", c=sort.factory)
pm.menuItem(divider=True)
pm.menuItem(subMenu=True, to=True, l='Automation')
pm.menuItem(l="Batch NYS Teams", c=buildNys_ui)
pm.menuItem(l="Batch CFP Teams", c=buildPlayoff_ui)
pm.menuItem(l="Batch NYS Opens", c=playoffMatchupWin)
pm.menuItem(l="Batch SNF Teams", c=buildCity_ui)
pm.setParent(mmenu, menu=True)


pm.menuItem(divider=True)
pm.menuItem(subMenu=True, to=True, l='Asset Creation')
pm.menuItem(l="Make New Asset", c=asset.makeNew)
pm.menuItem(divider=True)
pm.menuItem(l="Geometry Sort Group / V-Ray OPG", c=vrayutils.makeObjectProperties)
pm.menuItem(l="Light Sort Group / V-Ray LSS", c=vrayutils.makeLightSelectSet)
pm.menuItem(l="Matte Assignment", c=vmt.main)
pm.menuItem(divider=True)
pm.menuItem(l="Check Model", c=lambda *args: asset.sanityCheck(report=True, model=True))
pm.menuItem(l="Check Shading", c=lambda *args: asset.sanityCheck(report=True, shading=True))
pm.menuItem(divider=True)
pm.menuItem(l="EXPORT ASSET", c=asset.export)

pm.setParent(mmenu, menu=True)

pm.menuItem(divider=True)
pm.menuItem(l="Sort Control / Load Team", c=sortControlWidget)
pm.menuItem(subMenu=True, to=True, l='Scene Setup')
pm.menuItem(l="Scene Setup", c=init_scene)
pm.menuItem(l="Reference Asset", c=lambda *args: asset.assetSelector(init=True, mode='reference'))
pm.menuItem(l="Import Asset", c=lambda *args: asset.assetSelector(init=True, mode='import'))
pm.menuItem(l="Remove and Reference", c=asset.swapImportWithReference)
pm.menuItem(l="Remove and Import", c=asset.swapReferenceWithImport)
pm.setParent(mmenu, menu=True)

pm.menuItem(divider=True)
pm.menuItem(subMenu=True, to=True, l='Animation Tools')
pm.menuItem(l="Export Atom", c=anim.exportAtom)
pm.menuItem(l="Import Atom", c=anim.importAtom)
pm.menuItem(l="Export Camera", c=anim.exportCamera)
pm.menuItem(l="Import Camera", c=anim.importCamera)
pm.menuItem(l="Export Alembic", c=anim.exportAbc)





