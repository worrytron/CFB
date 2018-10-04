# Built-in packages
import time
from os import makedirs
from os import mkdir
from os.path import exists
from os.path import split
from os.path import join
from os.path import dirname
from os.path import basename

# Nuke packages
import nuke
import threading, thread

# External packages
from pipeline import cfb
from pipeline.nuke import submit
import pipeline.database.team as t

reload(t)
reload(submit)

DEFAULT_CPUS = 95

# Modify gvars for nuke-friendliness
TEAMS_ASSET_DIR = cfb.TEAMS_ASSET_DIR.replace('\\','/')

BASE_OUTPUT_DIR = cfb.ANIMATION_PROJECT_DIR.replace('\\','/')

# Node names from Nuke
MASTER_CTRL = "MASTER_CTRL"
MASTER_WRITE = "MASTER_WRITE"

# Split matchup write nodes
SPLIT_WRITE_NODES = [
    "WRITE_HOME_FILL",
    "WRITE_AWAY_FILL",
    "WRITE_HOME_MATTE"
    ]

PRIMARY_LOGO_READ = 'READ_{}_LOGO'
SECONDARY_LOGO_READ = 'READ_{}_POD_TWO'
TERTIARY_LOGO_READ = 'READ_{}_POD_THREE'
BANNER_LOGO_READ = 'READ_{}_BANNER'

EVENT_LOGO_READS = [
    'READ_{}_SUNSET',
    'READ_{}_NIGHT',
    'READ_{}_UTIL'
    ]

STUDIO_LOGO_READS = [
    'READ_{}_NOON',
    'READ_{}_UTIL'
    ]

CITY_LOGO_READS = [
    'READ_{}_NIGHT',
    'READ_{}_UTIL'
    ]

#############################################################################
## LOAD TEAM FUNCTIONS ######################################################
#############################################################################

def loadTeam(location, tricode=None, renders=False, multi=False):
    m_ctrl = nuke.toNode(MASTER_CTRL)

    if not (tricode):
        tricode = m_ctrl.knob('{}_team'.format(location)).getValue()
    elif (tricode):
        m_ctrl.knob('{}_team'.format(location)).setValue(tricode)

    team = t.Team(tricode)

    if not (multi):
        m_ctrl.knob('{}_sign'.format(location)).setValue(team.signNum)
        m_ctrl.knob('{}_region'.format(location)).setValue(int(team.matteNum))
        if location == 'home':
            m_ctrl.knob('sky').setValue(int(team.skyNum))

        selectRegions(location, team)
        selectSkies(location, team)
        selectSigns(location, team)

    selectColors(location, team)
    selectColorVariants(location, team)
    selectTeamLogo(location, team)
    selectTeamBanner(location, team)
    selectTeamPodTwo(location, team)
    selectTeamPodThree(location, team)

    if (renders):
        selectLogoRender(location, team)

def renameSave(matchup=False, multi=False):
    m_ctrl         = nuke.toNode(MASTER_CTRL)
    deliverable    = m_ctrl.knob('deliverable').getValue()
    scene          = nuke.root().name()
    #scene_dir_name = dirname(scene) + '/TEAMS'
    scene_dir_name = join(cfb.ANIMATION_PROJECT_DIR, deliverable, 'nuke', 'TEAMS')


    ## I.e. if only a team name or matchup is needed to version the file out (most common case)
    if not (multi):
        tricode = m_ctrl.knob('home_team').getValue()
        if (matchup):
            away_tricode = m_ctrl.knob('away_team').getValue()
            tricode += '_{}'.format(away_tricode)

        scene_name = deliverable + ('_{}.nk'.format(tricode))


    ## "MULTI" is a total hack and only used in a few scenes in the Playoff opens ...
    if (multi):
        event, bowl = getBowlEventFromScene()

        if (bowl):
            scene_name = deliverable + ('_{}_{}.nk'.format(event.upper(), bowl.upper()))

        else:
            scene_name = deliverable + ('_{}.nk'.format(event.upper()))


    if not exists(scene_dir_name):
        mkdir(scene_dir_name)

    out_path = join(scene_dir_name, scene_name)

    nuke.scriptSaveAs(out_path)

def quickSubmit(*a):
    nuke.scriptSave()
    frame_range = '{0}-{1}'.format(nuke.root().firstFrame(), nuke.root().lastFrame())
    scene_name  = basename(nuke.root().name())
    submit.singleNode(scene_name, nuke.root().name(), frame_range, '5000', '8', 'MASTER_WRITE') 

def selectColors(location, team):    
    primary = convertColor(team.primary, toFloat=True)
    secondary = convertColor(team.secondary, toFloat=True)

    m_ctrl = nuke.toNode(MASTER_CTRL)
    
    try:
        m_ctrl.knob('{}_primary'.format(location)).setValue(primary)
        m_ctrl.knob('{}_secondary'.format(location)).setValue(secondary)
    except: pass

def selectColorVariants(location, team):
    m_ctrl = nuke.toNode(MASTER_CTRL)

    #try:
    m_ctrl.knob('{}_bboard_color'.format(location)).setValue(team.billboard)
    m_ctrl.knob('{}_neon_color'.format(location)).setValue(team.neon)
    #except: pass

def selectRegions(location, team):    
    m_ctrl = nuke.toNode(MASTER_CTRL)
    try:
        m_ctrl.knob('{}_region'.format(location)).setValue( team.matteNum )
    except: pass

def selectSkies(location, team):    
    m_ctrl = nuke.toNode(MASTER_CTRL)
    try:
        m_ctrl.knob('sky').setValue( team.skyNum )
    except: pass

def selectSigns(location, team):    
    m_ctrl = nuke.toNode(MASTER_CTRL)
    try:
        m_ctrl.knob('{}_sign'.format(location)).setValue( team.signNum )
    except: pass

def selectTeamLogo(location, team):
    try:
        logoReadNode = nuke.toNode(PRIMARY_LOGO_READ.format(location.upper()))
        logoReadNode.knob('file').setValue(team2DAssetString(team.tricode, 1))
    except: pass

def selectTeamPodTwo(location, team):
    try:
        podTwoReadNode = nuke.toNode(SECONDARY_LOGO_READ.format(location.upper()))
        podTwoReadNode.knob('file').setValue(team2DAssetString(team.tricode, 2))
    except: pass

def selectTeamPodThree(location, team):
    try:
        podThreeReadNode = nuke.toNode(TERTIARY_LOGO_READ.format(location.upper()))
        podThreeReadNode.knob('file').setValue(team2DAssetString(team.tricode, 3))
    except: pass

def selectTeamBanner(location, team):
    try:
        bannerReadNode = nuke.toNode(BANNER_LOGO_READ.format(location.upper()))
        bannerReadNode.knob('file').setValue(team2DAssetString(team.tricode, 4))
    except: pass

def selectLogoRender(location, team):
    m_ctrl  = nuke.toNode(MASTER_CTRL)

    package = m_ctrl.knob('tod').getValue()

    logo_render_reads = {
        0.0: STUDIO_LOGO_READS,
        1.0: EVENT_LOGO_READS,
        2.0: EVENT_LOGO_READS,
        3.0: CITY_LOGO_READS,
        4.0: CITY_LOGO_READS,
        5.0: EVENT_LOGO_READS,
        6.0: EVENT_LOGO_READS
        }[package]

    for rn in logo_render_reads:
        rn = rn.format(location.upper())
        rn = nuke.toNode(rn.format(location.upper()))
        render_path = rn.knob('file').getValue().split('/')
        render_path[-3] = team.tricode
        new_path = '/'.join(render_path)

        rn.knob('file').setValue(new_path)

def selectBowlRender():
    m_ctrl = nuke.toNode(MASTER_CTRL)

    bowl   = m_ctrl.knob('bowl_select').getValue()

    bowl_name = {
        0.0: 'SUGAR',
        1.0: 'ROSE',
        2.0: 'ORANGE',
        3.0: 'COTTON',
        4.0: 'PEACH',
        5.0: 'FIESTA',
        6.0: 'CHAMP'
        }[bowl]

    for rn in ['BOWL_TEAMS_BTY','BOWL_TEAMS_UTIL']:
        rn = nuke.toNode(rn)
        render_path = rn.knob('file').getValue().split('/')
        render_path[-3] = bowl_name
        new_path = '/'.join(render_path)

        rn.knob('file').setValue(new_path)

#############################################################################
## HELPER FUNCTIONS #########################################################
#############################################################################

def convertColor( rgb_tuple, toFloat=True, toInt=False ):
    def __clamp(value):
        if value < 0: return 0
        if value > 255: return 255

    if toFloat:
        out_r = (1.0/255) * rgb_tuple[0]
        out_g = (1.0/255) * rgb_tuple[1]
        out_b = (1.0/255) * rgb_tuple[2]
        return (out_r, out_g, out_b)
    if toInt:
        out_r = __clamp(int(255 * rgb_tuple[0]))
        out_g = __clamp(int(255 * rgb_tuple[1]))
        out_b = __clamp(int(255 * rgb_tuple[2]))
        return (out_r, out_g, out_b)

def writeThread(write_node, start_frame, end_frame):
    nuke.executeInMainThread(nuke.execute, args=(write_node, start_frame, end_frame, 1), kwargs={'continueOnError':True})

def team2DAssetString(tricode, num):
    asset = '{0}{1}/includes/{2}_0{3}.png'.format(TEAMS_ASSET_DIR, tricode, tricode, str(num))
    return asset

def setOutputPath(create_dirs=False, matchup=False, jumbo=False, quad=False):
    m_ctrl = nuke.toNode(MASTER_CTRL)
    m_write = nuke.toNode(MASTER_WRITE)
    
    package     = m_ctrl.knob('tod').getValue()
    deliverable = m_ctrl.knob('deliverable').getValue()

    # Container list for all version tokens
    version_tokens = []

    base_dir = "{}/{}/render_2d/TEAMS".format(BASE_OUTPUT_DIR, deliverable)

    # Get show ID tag
    show_str = {
        0.0: 'STUDIO',
        1.0: 'CFB',
        2.0: 'PRIMETIME',
        3.0: 'SNF',
        4.0: 'PRIMETIME',
        5.0: 'NYS',
        6.0: 'CHAMP'
        }[package]
    if not (package == 0.0) or (package == 5.0): version_tokens.append(show_str)

    # Get teams
    home_team   = m_ctrl.knob('home_team').getValue()
    if (matchup): 
        away_team = m_ctrl.knob('away_team').getValue()
    else: away_team = ''

    if (matchup) and not (jumbo):
        version_tokens.append(away_team)

    version_tokens.append(home_team)
    version_str = '_'.join(version_tokens)
    version_str = version_str.lstrip('_')
    version_str = version_str.rstrip('_')

    if not (jumbo):
        version_dir = base_dir + '/' + version_str
        out_str = '{}/{}_{}.%04d.png'.format(version_dir, deliverable, version_str)  

        if (create_dirs):
            if not exists(version_dir):
                makedirs(version_dir)
        
        m_write.knob('file').setValue(out_str)

        return


    elif (jumbo):

        try:
            test = nuke.toNode('WRITE_HOME_MATTE')
        except: pass

        home_dir = base_dir + '/' + version_str + '_HOME_FILL'
        home_str = '{}/{}_{}_HOME.%04d.png'.format(home_dir, deliverable, version_str)  
        away_dir = base_dir + '/' + version_str + '_AWAY_FILL'
        away_str = '{}/{}_{}_AWAY.%04d.png'.format(away_dir, deliverable, version_str)  
        if (test):
            matte_dir = base_dir + '/' + version_str + '_HOME_MATTE'
            matte_str = '{}/{}_{}_MATTE.%04d.png'.format(matte_dir, deliverable, version_str)  

        if (create_dirs):
            if not exists(home_dir):
                makedirs(home_dir)
            if not exists(away_dir):
                makedirs(away_dir)
            if (test):
                if not exists(matte_dir):
                    makedirs(matte_dir)

        nuke.toNode('WRITE_HOME_FILL').knob('file').setValue(home_str)
        nuke.toNode('WRITE_AWAY_FILL').knob('file').setValue(away_str)
        if test:
            test.knob('file').setValue(matte_str)

        return

def setOutputPathMulti(create_dirs=False):
    m_ctrl = nuke.toNode(MASTER_CTRL)
    m_write = nuke.toNode(MASTER_WRITE)
    deliverable = m_ctrl.knob('deliverable').getValue()
    event, bowl = getBowlEventFromScene()

    base_dir = "{}/{}/render_2d/TEAMS".format(BASE_OUTPUT_DIR, deliverable)
    
    if (bowl):
        version_dir = base_dir + '/' + bowl.upper()
        out_str = '{}/{}_{}.%04d.png'.format(version_dir, deliverable, bowl.upper())  
    else:
        version_dir = base_dir + '/' + event.upper()
        out_str = '{}/{}_{}.%04d.png'.format(version_dir, deliverable, event.upper())  



    if (create_dirs):
        if not exists(version_dir):
            makedirs(version_dir)
    
    m_write.knob('file').setValue(out_str)

    return

def getBowlEventFromScene():
    m_ctrl = nuke.toNode(MASTER_CTRL)

    event_idx = m_ctrl.knob('event_select').getValue()
    bowl_idx = m_ctrl.knob('bowl_select').getValue()

    event = {
        0: 'NYS',
        1: 'Playoff',
        2: 'Gameday',
        3: 'Championship'
        }[event_idx]

    bowl = {
        0: 'Sugar',
        1: 'Rose',
        2: 'Orange',
        3: 'Cotton',
        4: 'Peach',
        5: 'Fiesta',
        6: 'Champ'
        }[bowl_idx]

    if event_idx != 2:
        return (event, bowl)

    elif event_idx == 2:
        return (event, None)

#############################################################################
## GENERAL AUTOMATION #######################################################
#############################################################################

def createTeamScenes(team_list, range_, submit_to_farm=True, matchup=False, jumbo=False):
    m_ctrl = nuke.toNode(MASTER_CTRL)
    deliverable = m_ctrl.knob('deliverable').getValue()
    package     = m_ctrl.knob('tod').getValue()
    out_dir = join(BASE_OUTPUT_DIR, deliverable, 'nuke', 'TEAMS')
    if not exists(out_dir): mkdir(out_dir)

    for team in team_list:
        if package == 2:
            scene_name = '{}_{}_{}.nk'.format(deliverable, 'PRIMETIME', team)
        else:
            scene_name = '{}_{}.nk'.format(deliverable, team)

        scene_path = join(out_dir, scene_name)

        loadTeam('home', team, renders=True) 
        try: loadTeam('away', team, renders=True)
        except: pass
        setOutputPath(create_dirs=True, matchup=matchup, jumbo=jumbo)

        nuke.scriptSaveAs(scene_path, 1)
        time.sleep(1)

        if submit_to_farm:
            
            if not matchup:
                submit.singleNode(
                    (deliverable + ' - ' + team),
                    scene_path,
                    range_,
                    '5000',
                    'MASTER_WRITE')
            
            elif matchup:
                submit.singleNode(
                    (deliverable + ' - ' + team + ' HOME'),
                    scene_path,
                    range_,
                    '5000',
                    'WRITE_HOME_FILL')
                submit.singleNode(
                    (deliverable + ' - ' + team + ' AWAY'),
                    scene_path,
                    range_,
                    '5000',
                    'WRITE_AWAY_FILL') 
                
                test = nuke.toNode('WRITE_HOME_MATTE')
                if test:               
                    submit.singleNode(
                        (deliverable + ' - ' + team + ' MATTE'),
                        scene_path,
                        range_,
                        '5000',
                        'WRITE_HOME_MATTE')

def teamLogoUpdate(team_list=None):
    report = ''

    if (team_list == None) or (team_list == ''):
        team_list = nuke.getInput('Enter tricodes, separated by commas:', '')
        if (team_list):
            team_list = team_list.split(',')

    # Deliverable name, frame range, matchup?, primetime?
    scenes = [
        ('CFB_E_MATCHUP_FE_01_ST', '1-75', True, True),
        ('CFB_E_MATCHUP_ENDSTAMP_01_ST', '1-300', True, True),
        ('CFB_S_MATCHUP_FE_01_ST', '1-83', True, False),
        ('CFB_E_TEAM_FE_01_ST', '1-75', False, True),
        ('CFB_E_TEAM_ENDSTAMP_01_ST', '1-300', False, True),
        ('CFB_S_TEAM_FE_01', '1-90', False, False),
        ('TEAM_LOGO_QUADS', '1-1', False, False)
        ]

    for scene in scenes:
        # Pull values from the scene list
        deliverable, frange, matchup, primetime = scene
        print deliverable
        
        # check that the _TOOLKIT.nk file exists for that deliverable
        file_name = '{}_TOOLKIT.nk'.format(deliverable)
        scene_path = join(cfb.ANIMATION_PROJECT_DIR, deliverable, 'nuke', file_name)
        
        # if it exists, do the business
        if exists(scene_path):
            nuke.scriptClear()
            nuke.scriptOpen(scene_path)
            createTeamScenes(team_list, frange, submit_to_farm=True, matchup=matchup, jumbo=matchup)
            report += '\nCOOL:  Successfully submitted nuke scene for {}'.format(deliverable)
        else:
            report += '\nERROR: Could not find toolkit nuke scene for {}'.format(deliverable)
            
        # Repeat the process with a PRIMETIME tag if this is a nighttime scene as well
        if (primetime):
            file_name = '{}_PRIMETIME_TOOLKIT.nk'.format(deliverable)
            scene_path = join(cfb.ANIMATION_PROJECT_DIR, deliverable, 'nuke', file_name)
        
            if exists(scene_path):
                nuke.scriptClear()
                nuke.scriptOpen(scene_path)
                createTeamScenes(team_list, frange, submit_to_farm=True, matchup=matchup, jumbo=matchup)
                report += '\nCOOL:  Successfully submitted nuke scene for {}_PRIMETIME'.format(deliverable)
            else:    
                report += '\nERROR: Could not find toolkit nuke scene for {}_PRIMETIME'.format(deliverable)

    print report

def nysBuild(team_list):
    report = ''

    # Deliverable name, frame range, matchup?, primetime?
    scenes = [
        ('CFB_E_NYS_TEAM_TRANS_01', '1-75', True, True),
        ('CFB_E_MATCHUP_ENDSTAMP_01_ST', '1-300', True, True),
        ('CFB_S_MATCHUP_FE_01_ST', '1-83', True, False),
        ('CFB_E_TEAM_FE_01_ST', '1-75', False, True),
        ('CFB_E_TEAM_ENDSTAMP_01_ST', '1-300', False, True),
        ('CFB_S_TEAM_FE_01', '1-90', False, False)
        ]

    for scene in scenes:
        # Pull values from the scene list
        deliverable, frange, matchup, primetime = scene
        print deliverable
        
        # check that the _TOOLKIT.nk file exists for that deliverable
        file_name = '{}_TOOLKIT.nk'.format(deliverable)
        scene_path = join(cfb.ANIMATION_PROJECT_DIR, deliverable, 'nuke', file_name)
        
        # if it exists, do the business
        if exists(scene_path):
            nuke.scriptClear()
            nuke.scriptOpen(scene_path)
            createTeamScenes(team_list, frange, submit_to_farm=True, matchup=matchup, jumbo=matchup)
            report += '\nCOOL:  Successfully submitted nuke scene for {}'.format(deliverable)
        else:
            report += '\nERROR: Could not find toolkit nuke scene for {}'.format(deliverable)
            
        # Repeat the process with a PRIMETIME tag if this is a nighttime scene as well
        if (primetime):
            file_name = '{}_PRIMETIME_TOOLKIT.nk'.format(deliverable)
            scene_path = join(cfb.ANIMATION_PROJECT_DIR, deliverable, 'nuke', file_name)
        
            if exists(scene_path):
                nuke.scriptClear()
                nuke.scriptOpen(scene_path)
                createTeamScenes(team_list, frange, submit_to_farm=True, matchup=matchup, jumbo=matchup)
                report += '\nCOOL:  Successfully submitted nuke scene for {}_PRIMETIME'.format(deliverable)
            else:    
                report += '\nERROR: Could not find toolkit nuke scene for {}_PRIMETIME'.format(deliverable)

    print report

#############################################################################
## WEDGE RENDER FUNCTIONS ###################################################
#############################################################################
def preRender(matchup=False, jumbo=False):
    m_ctrl = nuke.toNode(MASTER_CTRL)

    #matchup = bool(m_ctrl.knob('is_matchup').getValue())
    
    team_list = m_ctrl.knob('team_list').getValue().split(',')

    loadTeam('home', team_list[0], renders=True)
    if matchup: 
        loadTeam('away', team_list[0], renders=True)
    
    setOutputPath(create_dirs=True, matchup=True, jumbo=False)

def postRender():
    m_ctrl = nuke.toNode(MASTER_CTRL)
    m_write = nuke.toNode(MASTER_WRITE)

    #start_frame = m_ctrl.knob('start_frame').getValue()
    #end_frame = m_ctrl.knob('end_frame').getValue()

    team_list = m_ctrl.knob('team_list').getValue().split(',')
    del team_list[0]
    m_ctrl.knob('team_list').setValue(','.join(team_list))
    
    if len(team_list) == 0:
        return

    else:
        render_thread = threading.Thread(name='', target=writeThread, args=(m_write, 60, 60))
        render_thread.setDaemon(False)
        render_thread.start()

        while render_thread.isAlive():
            time.sleep(0.1)

def preRenderQuad():
    m_ctrl = nuke.toNode(MASTER_CTRL)
    m_write = nuke.toNode(MASTER_WRITE)

    team_list = m_ctrl.knob('team_list').getValue().split(',')

    loadTeam('home', team_list[0], renders=True)
   
    #setOutputPath(create_dirs=False, matchup=False, jumbo=False, quad=True)

    out_str = '{}/TEAM_LOGO_QUADS/render_2d/{}_QUAD.png'.format(BASE_OUTPUT_DIR, team_list[0])

    m_write.knob('file').setValue(out_str)

    return

def postRenderQuad():
    m_ctrl = nuke.toNode(MASTER_CTRL)
    m_write = nuke.toNode(MASTER_WRITE)

    #start_frame = m_ctrl.knob('start_frame').getValue()
    #end_frame = m_ctrl.knob('end_frame').getValue()

    team_list = m_ctrl.knob('team_list').getValue().split(',')
    del team_list[0]
    m_ctrl.knob('team_list').setValue(','.join(team_list))
    
    if len(team_list) == 0:
        return

    else:
        render_thread = threading.Thread(name='', target=writeThread, args=(m_write, 1, 1))
        render_thread.setDaemon(False)
        render_thread.start()

        while render_thread.isAlive():
            time.sleep(0.1)

def preFrame():
    pass

def postFrame():
    pass
