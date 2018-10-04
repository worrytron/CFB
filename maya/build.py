# Internal modules
import pymel.core as pm

# External modules
from pipeline import cfb
from pipeline.maya import asset
from pipeline.maya import sort
from pipeline.maya import project
from pipeline.maya import submit

from pipeline.database.team import Team
from pipeline.database.team import checkTeams
import pipeline.vray.utils as utils

# Built-in modules
import os.path
import re

reload(cfb)
reload(asset)
reload(sort)
reload(project)
reload(submit)


cluster = "/C"
priority = "5000"

##############################################################################
### CALLED FUNCTIONS #########################################################
##############################################################################
def factory( *a ):
    asset.reference(cfb.FACTORY_LIGHT_RIG, 'FACTORY')
    sc = sort.SortControl('Factory')
    sc.run()


### STADIUM PACKAGE ##########################################################
def quad(team, *a):
    ''' A full scene-building routine for 'quad' logo slicks '''
    loadTeamsLite(team, team)
    sorter = sort.SortControl('Quad')
    sorter.run()

    try:
        pm.PyNode('HOMELOGO:GEO_05').visibility.set(0)
        pm.PyNode('AWAYLOGO:GEO_05').visibility.set(0)
    except: pass
    try:
        pm.PyNode('HOMELOGO:GEO_06').visibility.set(0)
        pm.PyNode('AWAYLOGO:GEO_06').visibility.set(0)
    except: pass

    v_ray = pm.PyNode('vraySettings')
    v_ray.fileNamePrefix.set("""TEAMS/{0}/%l/%l.#""".format(team))

    scene = project.Scene()
    scene.rename(team)


def singleTeam(tricode, package):
    ''' A full scene-building routine for single-team elements.'''
    #load in the new team
    loadTeamsStadium(tricode, diagnostic=False, clean=True)
    #sort
    sort.sceneTeardown()
    sc = sort.SortControl('Single_Team_{}'.format(package.upper()))
    sc.run()
    #change output path
    vrs = pm.PyNode('vraySettings')
    vrs.fileNamePrefix.set('TEAMS/{}/%l/%l.#'.format(tricode)) 
    #rename / save scene
    scene = project.Scene()
    scene.rename(tricode)


def splitMatchup(tricode, package):
    ''' A full scene-building routine for single-team elements.'''
    #load in the new team
    loadTeamsStadium(tricode, tricode, diagnostic=False, clean=True)
    #sort
    sort.sceneTeardown()
    sc = sort.SortControl('Split_Matchup_{}'.format(package.upper()))
    sc.run()
    #change output path
    vrs = pm.PyNode('vraySettings')
    vrs.fileNamePrefix.set('TEAMS/{}/%l/%l.#'.format(tricode)) 
    #rename / save scene
    scene = project.Scene()
    scene.rename(tricode)


### BLUE CITY PACKAGE ########################################################
def singleTeamCity(tricode):
    ''' A full scene-building routine for single-team CITY elements.'''
    loadTeamsLite(tricode)
    #sort
    sort.sceneTeardown()
    sc = sort.SortControl('Single_Team_CITY')
    sc.run()
    # change output path
    vrs = pm.PyNode('vraySettings')
    vrs.fileNamePrefix.set('TEAMS/{}/%l/%l.#'.format(tricode))
    # rename / save scene
    scene = project.Scene()
    scene.rename(tricode)


def splitMatchupCity(tricode):
    ''' A full scene-building routine for single-team CITY elements.'''
    loadTeamsLite(tricode, tricode)
    #sort
    sort.sceneTeardown()
    sc = sort.SortControl('Matchup_CITY')
    sc.run()
    # change output path
    vrs = pm.PyNode('vraySettings')
    vrs.fileNamePrefix.set('TEAMS/{}/%l/%l.#'.format(tricode))
    # rename / save scene
    scene = project.Scene()
    scene.rename(tricode)


### NEW YEAR'S SIX PACKAGE ###################################################
def singleTeamNYS(tricode):
    ''' A full scene-building routine for single-team NYS elements.'''
    loadTeamsNYS(tricode)
    # sort
    sort.sceneTeardown()
    sc = sort.SortControl('Single_Team_PLAYOFF_NYS')
    sc.run()
    # change output path
    vrs = pm.PyNode('vraySettings')
    vrs.fileNamePrefix.set('TEAMS/{}/%l/%l.#'.format(tricode))
    # rename / save scene
    scene = project.Scene()
    scene.rename(tricode)


def splitMatchupNYS(tricode):
    ''' A full scene-building routine for single-team elements.'''
    #load in the new team
    loadTeamsNYS(tricode, tricode, diagnostic=False, clean=True)
    #sort
    sort.sceneTeardown()
    sc = sort.SortControl('Split_Matchup_NYS')
    sc.run()
    #change output path
    vrs = pm.PyNode('vraySettings')
    vrs.fileNamePrefix.set('TEAMS/{}/%l/%l.#'.format(tricode)) 
    #rename / save scene
    scene = project.Scene()
    scene.rename(tricode)


### PLAYOFF PACKAGE ##########################################################
def singleTeamPlayoff(tricode):
    ''' A full scene-building routine for single-team NYS elements.'''
    loadTeamsLite(tricode, playoff=True)
    # sort
    sort.sceneTeardown()
    sc = sort.SortControl('Single_Team_PLAYOFF_NYS')
    sc.run()
    # change output path
    vrs = pm.PyNode('vraySettings')
    vrs.fileNamePrefix.set('TEAMS/{}/%l/%l.#'.format(tricode))
    # rename / save scene
    scene = project.Scene()
    scene.rename(tricode)    


def splitMatchupPlayoff(tricode):
    ''' A full scene-building routine for single-team CITY elements.'''
    loadTeamsLite(tricode, tricode, playoff=True)
    #sort
    sort.sceneTeardown()
    sc = sort.SortControl('Split_Matchup_NYS')
    sc.run()
    # change output path
    vrs = pm.PyNode('vraySettings')
    vrs.fileNamePrefix.set('TEAMS/{}/%l/%l.#'.format(tricode))
    # rename / save scene
    scene = project.Scene()
    scene.rename(tricode)


### MULTI-TEAM SCENE #########################################################
def multiTeam(tricode_list, playoff=False, force_name=None):

    if (playoff):
        attachments = getMultiTeamAttachments()

        if len(attachments) > len(tricode_list):
            pm.warning('ERROR  Not enough teams specified ({} minimum).  Aborting...'.format(len(attachments)))
            return

        if len(attachments) < len(tricode_list):
            pm.warning('ERROR  Too many teams specified ({} maximum).  Aborting...'.format(len(attachments)))
            return
    
        for idx, loc in enumerate(attachments):
            print attachments[idx]
            attachments[idx] = loc[:-7].strip()

        for idx, tricode in enumerate(tricode_list):
            loadAssetsLite(tricode, attachments[idx], playoff=playoff)


    elif not (playoff):
        namespaces = getMultiTeamAttachments(references=True)

        if len(namespaces) > len(tricode_list):
            pm.warning('ERROR  Not enough teams specified ({} minimum).  Aborting...'.format(len(namespaces)))
            return

        if len(namespaces) < len(tricode_list):
            pm.warning('ERROR  Too many teams specified ({} maximum).  Aborting...'.format(len(namespaces)))
            return

        for idx, namespace in enumerate(namespaces):
            namespaces[idx] = namespace[:-4].strip()

        for idx, tricode in enumerate(tricode_list):
            loadAssetsNYS(tricode, namespaces[idx])


    sort.sceneTeardown()
    sc = sort.SortControl('Multi-Team (NYS / CHAMP)')
    sc.run()

    if project.isScene():
        scene = project.Scene()    
        scene.rename(name=force_name, save=False)

        prefix = scene.custom_string
        vrs = pm.PyNode('vraySettings')
        vrs.fileNamePrefix.set('{}/%l/%l.#'.format(prefix))
        
        scene.save()
        return
    else:
        return


### AUTOMATION ###############################################################
def updateTeamLogo(tricode):
    # Get list of skeleton scenes and iterate over them
    skeletons = [('CFB_E_TEAM_FE_01_ST', 'single', '1-75'),
                 ('CFB_E_TEAM_ENDSTAMP_01_ST', 'single', 'stadium', '1-300'),
                 ('CFB_S_TEAM_FE_01', 'single', 'studio', '1-90'),
                 ('CFB_E_MATCHUP_FE_01_ST', 'split', 'stadium', '1-75'),
                 ('CFB_E_MATCHUP_ENDSTAMP_01_ST', 'split', 'jumbo', '1-300'),
                 ('CFB_S_MATCHUP_FE_01', 'split', '1-83'),
                 ('TEAM_LOGO_QUADS', 'quad', '1-2')
                ]
    
    report = ''
    flag = 0

    for skeleton in skeletons:
        deliverable, type_, package, frange = skeleton

        # generate path for skeleton scene
        file_name = deliverable + '_SKELETON' + '.mb'
        file_path = os.path.join(cfb.ANIMATION_PROJECT_DIR, deliverable, 'maya', 'scenes', file_name)

        if not os.path.exists(file_path):
            #print file_path
            flag = 1
            report += '\nWARNING could not find {}.'.format(deliverable)
            continue

        try:
            # open scene
            project.Scene.open(file_=file_path, force=True)
            # build scene with new logo, based on type
            if type_ == 'single':
                singleTeam(tricode, package)
            elif type_ == 'split':
                splitMatchup(tricode, package)
            elif type_ == 'quad':
                quad(tricode)
            ## submit to farm
            submit.autoSubmitAll(frange, '/C', '', priority)
            ## append to report
            report += '\nSuccessfully modified & submitted {} update for {}'.format(deliverable, tricode)
        except:
            flag = 1
            report += '\nWARNING failed to update {} for {}'.format(deliverable, tricode)

    print report

    if not flag:
        pm.warning('Build Scene  Update team logo operation completed with no errors.  Check the farm for your submissions.')
    elif flag:
        pm.warning('Build Scene  ERROR updating team logo.  Check script editor for details.')


def cityWeeklyBuild(tricode_list):
    report = ''
    flag = 0
    # List order:  SNF - away, home; PT - away, home
    skeletons = [('CFB_E_TEAM_FE_02', 'single', '1-150'),
                 ('CFB_E_TEAM_ENDSTAMP_02', 'single', '1-600'),
                 ('CFB_E_MATCHUP_FE_02', 'split', '1-150'),
                 ('CFB_E_MATCHUP_ENDSTAMP_02', 'split', '1-600'),
                 ('CFB_E_B2B_03_C', 'split', '1-150'),
                 ('CFB_E_VIZ_BUMP_02', 'split', '1-150'),
                 ('CFB_E_OPEN_02_C_SH0010', 'split', '1-59'),
                 ('CFB_E_OPEN_02_C_SH0020', 'single', '1-60'),
                 ('CFB_E_OPEN_02_C_SH0050', 'single', '1-43'),
                 ('CFB_E_OPEN_02_C_SH0080', 'split', '1-130'),
                 ('CFB_E_MATCHUP_ENDSTAMP_04', 'split', '1-600'),
                 ('CFB_E_TEAM_FE_03', 'single', '1-90'),
                 ('CFB_E_TEAM_ENDSTAMP_03_C', 'single', '1-300')
                 ]

    for tricode in tricode_list:
        for skeleton in skeletons:

            deliverable, type_, frange = skeleton

            file_name = deliverable + '_SKELETON.mb'
            file_path = os.path.join(cfb.ANIMATION_PROJECT_DIR, deliverable, 'maya', 'scenes', file_name)

            if not os.path.exists(file_path):
                flag = 1
                report += '\nWARNING could not find {}.'.format(deliverable)
                continue

            try:
                project.Scene.open(file_=file_path, force=True)
                if type_ == 'single':
                    singleTeamCity(tricode)
                elif type_ == 'split':
                    splitMatchupCity(tricode)
                submit.autoSubmitAll(frange, cluster, '', priority)
                report += '\nSuccessfully modified & submitted {} update for {}'.format(deliverable, tricode)
            except:
                flag = 1
                report += '\nWARNING failed to update {} for {}'.format(deliverable, tricode)

    print report

    if not flag:
        pm.warning('Build Scene  Update team logo operation completed with no errors.  Check the farm for your submissions.')
    elif flag:
        pm.warning('Build Scene  ERROR updating team logo.  Check script editor for details.')


def nysBuild(tricode_list):
    report = ''
    flag = 0
    # 
    skeletons = [('CFP_E_NYS_TEAM_TRANS_01', 'single', '1-60'),
                 ('CFP_E_NYS_TEAM_ENDSTAMP_01', 'single', '45-345'),
                 ('CFP_E_NYS_TEAM_ROLLOUT_FE_01', 'single', '1-60'),
                 ('CFP_E_NYS_PLAYER_ENDSTAMP_01', 'single', '1-300'),
                 #('CFP_E_NYS_MATCHUP_REJOIN_01', 'split', '1-150'),
                 ('CFP_E_NYS_MATCHUP_TRANS_01', 'split', '1-60'),
                 ('CFP_E_NYS_MATCHUP_TRANS_02', 'split', '1-120'),
                 ('CFP_E_NYS_MATCHUP_TRANS_03', 'split', '1-75'),
                 ('CFP_E_NYS_MATCHUP_ENDSTAMP_01', 'split', '1-150'),
                 ('CFP_E_NYS_MATCHUP_ROLLOUT_FE_01', 'split', '1-150')
                 ]

    for tricode in tricode_list:
        for skeleton in skeletons:

            deliverable, type_, frange = skeleton

            file_name = deliverable + '_SKELETON.mb'
            file_path = os.path.join(cfb.ANIMATION_PROJECT_DIR, deliverable, 'maya', 'scenes', file_name)

            if not os.path.exists(file_path):
                flag = 1
                report += '\nWARNING could not find {}.'.format(deliverable)
                continue

            try:
                project.Scene.open(file_=file_path, force=True)
                if type_ == 'single':
                    singleTeamNYS(tricode)
                elif type_ == 'split':
                    splitMatchupNYS(tricode)
                submit.autoSubmitAll(frange, cluster, '', priority)
                report += '\nSuccessfully modified & submitted {} update for {}'.format(deliverable, tricode)
            except:
                flag = 1
                report += '\nWARNING failed to update {} for {}'.format(deliverable, tricode)

    print report

    if not flag:
        pm.warning('Build Scene  Update team logo operation completed with no errors.  Check the farm for your submissions.')
    elif flag:
        pm.warning('Build Scene  ERROR updating team logo.  Check script editor for details.')


def nysOpensBuild(matchup_dict, cgd, nys, playoff):
    report = ''
    flag = 0
    # 
    nys_skeletons = {
                    ('CFP_E_OPEN_SHOT_010', 'nys', 'away', '1-184'),
                    ('CFP_E_OPEN_SHOT_020', 'nys', 'home', '1-120'),
                    ('CFP_E_OPEN_SHOT_050', 'nys', 'matchups', '1-200')
                    }

    cgd_skeletons = {
                    ('CFP_E_OPEN_SHOT_010', 'cgd', 6, '1-184'),
                    ('CFP_E_OPEN_SHOT_020', 'cgd', 3, '1-120'),
                    ('CFP_E_OPEN_SHOT_030', 'cgd', 3, '1-122')
                    }

    playoff_skeletons = {
                    ('CFP_E_OPEN_SHOT_050', 'playoff', 'matchups', '1-200')
                    }

    # Make a list of all tricodes listed in the dictionary
    all_teams_list = []
    itr = 0

    for bowl in matchup_dict:
        all_teams_list.append(matchup_dict[bowl][0])
        all_teams_list.append(matchup_dict[bowl][1])
    # and check that they all exist...
    if not checkTeams(all_teams_list):
        return False

    nys_dict = {}
    playoff_dict = {}

    for bowl in matchup_dict:
        away_team, home_team, playoff_flag = matchup_dict[bowl]
        if not playoff_flag:
            nys_dict[bowl] = matchup_dict[bowl]
        elif playoff_flag:
            playoff_dict[bowl] = matchup_dict[bowl]

    if (playoff):
        for bowl in playoff_dict:

            print '\n\nStarting batching for {} BOWL\n'.format(bowl)

            other_bowl = playoff_dict.copy()

            away_team, home_team, playoff_flag = other_bowl.pop(bowl)

            for b in other_bowl:
                o_away_team, o_home_team, playoff_flag = other_bowl[b]

            team_list = [o_away_team,
                         o_home_team,
                         away_team,
                         home_team]
            
            print team_list 

            for skeleton in playoff_skeletons:

                # Parse skeleton infomration
                deliverable, type_, team_sel, frange = skeleton

                # Build the name of the skeleton scene
                file_name = deliverable + '_' + type_.upper() + '_SKELETON.mb'
                file_path = os.path.join(cfb.ANIMATION_PROJECT_DIR, deliverable, 'maya', 'scenes', file_name)


                # Check that the skeleton exists
                if not os.path.exists(file_path):
                    flag = 1
                    report += '\nWARNING could not find {}.'.format(deliverable)
                    continue

                # DO THE BUSINESS
                try:
                    project.Scene.open(file_=file_path, force=True)
                    if team_sel == 'matchups':
                        multiTeam(team_list, playoff=True, force_name=bowl)

                    submit.autoSubmitAll(frange, cluster, '', priority)

                    report += '\nSuccessfully modified & submitted {} scene for {}'.format(deliverable, bowl)
                except:
                    flag = 1

    # NYS elements
    if (nys):
        for bowl in nys_dict:

            print '\n\nStarting batching for {} BOWL\n'.format(bowl)

            other_bowls = nys_dict.copy()

            # We extract the information about THIS bowl game
            away_team, home_team, playoff_flag = other_bowls.pop(bowl)
            # By popping we create a list of the other bowl matchups

            # Skip playoff matchups!!!!
            if playoff_flag == True:
                continue

            # We convert those other bowl matchups into an ordered list
            team_list = []
            for ob in other_bowls:
                team_list.append(other_bowls[ob][0])
                team_list.append(other_bowls[ob][1])

            # Now, with that information, we put our current matchup at the end
            team_list += [away_team, home_team]


            for skeleton in nys_skeletons:

                # Parse skeleton infomration
                deliverable, type_, team_sel, frange = skeleton

                # Build the name of the skeleton scene
                file_name = deliverable + '_' + type_.upper() + '_SKELETON.mb'
                file_path = os.path.join(cfb.ANIMATION_PROJECT_DIR, deliverable, 'maya', 'scenes', file_name)


                # Check that the skeleton exists
                if not os.path.exists(file_path):
                    flag = 1
                    report += '\nWARNING could not find {}.'.format(deliverable)
                    continue

                # DO THE BUSINESS
                try:
                    project.Scene.open(file_=file_path, force=True)
                    if team_sel == 'away':
                        multiTeam([away_team], playoff=False, force_name=bowl)
                    elif team_sel == 'home':
                        multiTeam([home_team], playoff=False, force_name=bowl)
                    elif team_sel == 'matchups':
                        multiTeam(team_list, playoff=False, force_name=bowl)

                    submit.autoSubmitAll(frange, cluster, '', priority)

                    report += '\nSuccessfully modified & submitted {} scene for {}'.format(deliverable, bowl)
                except:
                    flag = 1
                    report += '\nWARNING failed to build {} for {}'.format(deliverable, bowl)
 

    # Gameday only uses each team once, so we need to build a single list of teams and
    # pop elements out as needed
    if (cgd):
        for skeleton in cgd_skeletons:

            deliverable, type_, num_teams, frange = skeleton

            # GAMEDAY HAX
            # Using the # of teams specified from the skeleton dictionary, pop that number out and make a new list
            team_list = []
            for i in range(num_teams):
                team_list.append(all_teams_list.pop(0))

            print team_list

            # Build the name of the skeleton scene
            file_name = deliverable + '_' + type_.upper() + '_SKELETON.mb'
            file_path = os.path.join(cfb.ANIMATION_PROJECT_DIR, deliverable, 'maya', 'scenes', file_name)

            # Check that the skeleton exists
            if not os.path.exists(file_path):
                flag = 1
                report += '\nWARNING could not find {}.'.format(deliverable)
                continue

            # DO THE BUSINESS
            try:
                project.Scene.open(file_=file_path, force=True)
                multiTeam(team_list, playoff=False, force_name='GAMEDAY')
                submit.autoSubmitAll(frange, cluster, '', priority)

                report += '\nSuccessfully modified & submitted {} scene for GAMEDAY'.format(deliverable)
            except:
                flag = 1
                report += '\nWARNING failed to build {} for GAMEDAY'.format(deliverable)

    print report

    if not flag:
        pm.warning('Build Scene  Update team logo operation completed with no errors.  Check the farm for your submissions.')
    elif flag:
        pm.warning('Build Scene  ERROR updating team logo.  Check script editor for details.')


def playoffBuild(tricode_list):
    report = ''
    flag = 0
    # 
    skeletons = [('CFP_E_PLAYOFF_TEAM_TRANS_01', 'single', '1-60'),
                 ('CFP_E_PLAYOFF_TEAM_ENDSTAMP_01', 'single', '45-345'),
                 ('CFP_E_PLAYOFF_TEAM_ROLLOUT_FE_01', 'single', '1-60'),
                 ('CFP_E_PLAYOFF_PLAYER_ENDSTAMP_01', 'single', '1-300'),
                 #('CFP_E_PLAYOFF_MATCHUP_REJOIN_01', 'split', '1-150'),
                 ('CFP_E_PLAYOFF_MATCHUP_TRANS_01', 'split', '1-60'),
                 ('CFP_E_PLAYOFF_MATCHUP_TRANS_02', 'split', '1-120'),
                 ('CFP_E_PLAYOFF_MATCHUP_ENDSTAMP_01', 'split', '1-150'),
                 ('CFP_E_PLAYOFF_MATCHUP_ROLLOUT_FE_01', 'split', '1-150')
                 ]

    for tricode in tricode_list:
        for skeleton in skeletons:

            deliverable, type_, frange = skeleton

            file_name = deliverable + '_SKELETON.mb'
            file_path = os.path.join(cfb.ANIMATION_PROJECT_DIR, deliverable, 'maya', 'scenes', file_name)

            if not os.path.exists(file_path):
                flag = 1
                report += '\nWARNING could not find {}.'.format(deliverable)
                continue

            try:
                project.Scene.open(file_=file_path, force=True)
                if type_ == 'single':
                    singleTeamPlayoff(tricode)
                elif type_ == 'split':
                    splitMatchupPlayoff(tricode)
                submit.autoSubmitAll(frange, cluster, '', priority)
                report += '\nSuccessfully modified & submitted {} update for {}'.format(deliverable, tricode)
            except:
                flag = 1
                report += '\nWARNING failed to update {} for {}'.format(deliverable, tricode)

    print report

    if not flag:
        pm.warning('Build Scene  Update team logo operation completed with no errors.  Check the farm for your submissions.')
    elif flag:
        pm.warning('Build Scene  ERROR updating team logo.  Check script editor for details.')


##############################################################################
### CORE PROCEDURES ##########################################################
##############################################################################

### SINGLE-TEAM OPS ##########################################################
def loadAssetsStadium(tricode, location, diagnostic=False, clean=True):
    # Get team info from database
    """ Given a specific location (home/away), this function attempts to reference
        in a selected team's assets and attach them to respected 01, 05 and 06
        attachment points."""
    try:
        team = Team(tricode)
    except: 
        pm.warning('Build Scene  ERROR Could not find team in database.')
        return

    # Generate string for the name of the school's sign
    sign = 'SIGN_{0}'.format(team.sign.upper())
    # Generate string for the school's matte painting ID
    mp_id = str(team.matteNum).zfill(2)

    
    ''' LK SPECIFIC SECTION '''
    # The full path of this scene
    this_scene = pm.sceneName()
    # Split into tokens
    scene_token = this_scene.split('/')
    # 4th from the right is the project name
    this_project = scene_token[len(scene_token)-1].replace('_SKELETON.mb', '')
    ''' END LK '''


    # Create paths for signs / team logo / region / layout scenes
    sign_path = os.path.join(cfb.MAIN_ASSET_DIR, sign, (sign+'.mb'))
    logo_path = os.path.join(cfb.TEAMS_ASSET_DIR, team.tricode, (team.tricode+'.mb'))
    lgtrig_path = os.path.join(cfb.MAIN_ASSET_DIR, 'LIGHTING_BASE', 'LIGHTING_BASE.mb')
    
    if (diagnostic):
        print '\n'
        print '{} Team:   {}'.format(location, team.tricode)
        print 'Project:     {}'.format(this_project)
        print '{} Sign:   {}'.format(location, sign_path)
        print '{} Logo:   {}'.format(location, logo_path)
        print 'Light Rig:   {}'.format(lgtrig_path)


    # Check for missing files and print warnings
    if not os.path.exists(sign_path):
        pm.warning('Build Scene  WARNING could not find {0}'.format(sign_path))
        sign_path = None
    if not os.path.exists(logo_path):
        pm.warning('Build Scene  WARNING could not find {0}'.format(logo_path))
        logo_path = None
    if not os.path.exists(lgtrig_path):
        pm.warning('Build Scene  WARNING could not find {0}'.format(lgtrig_path))
        lgtrig_path = None

    if (diagnostic):
        return

    # Generate namespaces
    sign_nspc = '{0}SIGN'.format(location)
    logo_nspc = '{0}LOGO'.format(location)

    # Check for existing references
    sign_ref = None
    logo_ref = None

    # Get those reference nodess
    for ref in pm.listReferences():
        if ref.namespace == sign_nspc:
            sign_ref = ref

        elif ref.namespace == logo_nspc:
            logo_ref = ref

    # If there are references missing, force a clean run for simplicity's sake (i implore you)
    if (sign_ref) or (logo_ref) == None and clean == False:
        pm.warning('Build Scene  Existing reference not found.  Forcing clean reference.')
        clean = True

    # If the user has asked to do a clean reference of the asset, including attachment
    if (clean):
        # If there's already references in those namespaces, just delete them
        if (logo_ref): logo_ref.remove()
        if (sign_ref): sign_ref.remove()
        # Reference in the asset to the namespace
        if sign_path: asset.reference(sign_path, sign_nspc)
        if logo_path: asset.reference(logo_path, logo_nspc)

        # Attach them to their parent locators
        attachTeamToSign(location)
        attachSignToScene(location)

    # (If) there are already references in the namespaces, and the user is requesting
    # to replace the reference and maintain reference edits (dirty mode)
    elif not (clean):
        # If the right sign is already loaded, pass
        if (sign+'.mb') in sign_ref.path:
            pass
        # Or else replace the sign reference
        else:
            sign_ref.replaceWith(sign_path)
        # Same thing with school logos this time
        if (team.tricode+'.mb') in logo_ref.path:
            pass
        else:
            logo_ref.replaceWith(logo_path)

    # Cleanup foster parents
    try:
        sign_re = re.compile('{0}RNfosterParent.'.format(sign_nspc))
        logo_re = re.compile('{0}RNfosterParent.'.format(logo_nspc))

        pm.delete(pm.ls(regex=sign_re))
        pm.delete(pm.ls(regex=logo_re))
    except:
        pass


def loadAssetsLite(tricode, location, playoff=False, diagnostic=True):
    ''' Load the selected team logo (only) into the specificed 'location' (home/away)
        as a namespace.
        LITE version attaches only the logo to a locator called HOME_LOCATOR.'''

    try:
        team = Team(tricode)
    except:
        pm.warning('Build Scene  ERROR Could not find team in database.')
        return

    # Generate target logo path and namespace
    if not playoff:
        logo_path = os.path.join(cfb.TEAMS_ASSET_DIR, team.tricode, (team.tricode+'.mb'))
    elif playoff:
        logo_path = os.path.join(cfb.TEAMS_ASSET_DIR, (team.tricode + '_CHAMP'), (team.tricode+'_CHAMP.mb'))
    if not os.path.exists(logo_path):
        pm.warning('Build Scene  WARNING could not find {0}'.format(logo_path))
        return
    logo_nspc = '{}LOGO'.format(location)

    # Get existing reference nodes and kill them
    logo_ref = None
    for ref in pm.listReferences():
        if ref.namespace == logo_nspc:
            logo_ref = ref

    if (logo_ref): logo_ref.remove()

    # Reference the logo
    try:
        asset.reference(logo_path, logo_nspc)
    except:
        pm.warning('Build Scene  ERROR Could not reference {} logo.'.format(tricode))

    # Attach the logo
    try:
        attachTeamLite(location)
    except:
        pm.warning('Build Scene  ERROR Could not attach {} logo.'.format(tricode))       

    foster_re = re.compile('.RNfosterParent.')
    pm.delete(pm.ls(regex=foster_re))


def loadAssetsNYS(tricode, location, diagnostic=False, clean=True):
    # Get team info from database
    """ Given a specific location (home/away), this function attempts to reference
        in a selected team's assets and attach them to respected 01, 05 and 06
        attachment points."""
    try:
        team = Team(tricode)
    except: 
        pm.warning('Build Scene  ERROR Could not find team in database.')
        return

    
    ''' LK SPECIFIC SECTION '''
    # The full path of this scene
    this_scene = pm.sceneName()
    # Split into tokens
    scene_token = this_scene.split('/')
    # 4th from the right is the project name
    this_project = scene_token[len(scene_token)-1].replace('_SKELETON.mb', '')
    ''' END LK '''


    # Create paths for signs / team logo / region / layout scenes
    logo_path = os.path.join(cfb.TEAMS_ASSET_DIR, team.tricode, (team.tricode+'.mb'))
    

    if (diagnostic):
        print '\n'
        print '{} Team:   {}'.format(location, team.tricode)
        print 'Project:     {}'.format(this_project)
        print '{} Sign:   {}'.format(location, sign_path)
        print '{} Logo:   {}'.format(location, logo_path)
        print 'Light Rig:   {}'.format(lgtrig_path)


    # Check for missing files and print warnings
    if not os.path.exists(logo_path):
        pm.warning('Build Scene  WARNING could not find {0}'.format(logo_path))
        logo_path = None

    if (diagnostic):
        return

    # Generate namespaces
    sign_nspc = '{0}SIGN'.format(location)
    logo_nspc = '{0}LOGO'.format(location)

    # Check for existing references
    sign_ref = None
    logo_ref = None

    # Get those reference nodess
    for ref in pm.listReferences():
        if ref.namespace == logo_nspc:
            logo_ref = ref

    # If there are references missing, force a clean run for simplicity's sake (i implore you)
    if (logo_ref) == None and clean == False:
        pm.warning('Build Scene  Existing reference not found.  Forcing clean reference.')
        clean = True

    # If the user has asked to do a clean reference of the asset, including attachment
    if (clean):
        # If there's already references in those namespaces, just delete them
        if (logo_ref): logo_ref.remove()
        # Reference in the asset to the namespace
        if logo_path: asset.reference(logo_path, logo_nspc)

        # Attach them to their parent locators
        attachTeamToSign(location)

    # (If) there are already references in the namespaces, and the user is requesting
    # to replace the reference and maintain reference edits (dirty mode)
    elif not (clean):
        # Same thing with school logos this time
        if (team.tricode+'.mb') in logo_ref.path:
            pass
        else:
            logo_ref.replaceWith(logo_path)

    # Cleanup foster parents
    try:
        logo_re = re.compile('{0}RNfosterParent.'.format(logo_nspc))

        pm.delete(pm.ls(regex=logo_re))
    except:
        pass


### MATCHUP HELPERS ##########################################################
def loadTeamsStadium(home_team, away_team=None, diagnostic=False, clean=True, *a):
    loadAssetsStadium(home_team, 'HOME', diagnostic, clean)
    if away_team:
        loadAssetsStadium(away_team, 'AWAY', diagnostic, clean)
    return


def loadTeamsLite(home_team, away_team=None, playoff=False, *a):
    ''' A lite version of loadTeams that skips signs and major authoring steps,
        only loading a team primary logo and attaching it to a scene locator.'''
    loadAssetsLite(home_team, 'HOME', playoff)
    if away_team:
        loadAssetsLite(away_team, 'AWAY', playoff)
    return


def loadTeamsNYS(home_team, away_team=None, diagnostic=False, clean=True, *a):
    loadAssetsNYS(home_team, 'HOME', diagnostic, clean)
    if away_team:
        loadAssetsNYS(away_team, 'AWAY', diagnostic, clean)
    return


##############################################################################
### HELPER FUNCTIONS  ########################################################
##############################################################################
def getMultiTeamAttachments(references=False):
    ''' Used in multiTeam scenes -- gets a list of all attachment points'''

    attachments = []
    namespaces = []

    if not (references):    
        reg = re.compile(r"^TEAM_\d{2,3}_LOCATOR")

        locators = pm.ls(typ='locator')
        for idx, loc in enumerate(locators):
            if re.match(reg, str(loc)):
                attachments.append(loc.getParent())
            else: pass
        return sorted(attachments)


    elif (references):
        reg = re.compile(r"^TEAM_\d{2,3}_SIGN")
        
        references = pm.listReferences()
        for idx, ref in enumerate(references):
            if re.match(reg, ref.namespace):
                namespaces.append(ref.namespace)
            else: pass
        return sorted(namespaces)


def attachTeamLite(location):
    ''' Attaches a team logo to a locator called {LOCATION}_LOCATOR.'''
    location = location.upper()

    logo_namespace = '{0}LOGO'.format(location)

    logo_atch = None
    try:
        logo_atch = pm.PyNode('{0}LOGO:ATTACH_01'.format(location))
    except:
        pm.warning('Build Scene  ERROR Could not find logo attachment for {} team.'.format(location))

    # terrible, terrible hacking (for playoff elements)
    if 'TEAM' in location:
        location = location[:-1]

    scene_atch = None
    try:
        scene_atch = pm.PyNode('{0}_LOCATOR'.format(location))
    except:
        pm.warning('Build Scene  ERROR Could not find scene attachment for {} team.'.format(location))

    if (logo_atch) and (scene_atch):
        attach(scene_atch, logo_atch)
    return


def attachTeamToSign(location, n_scaleable=False):
    ''' Attaches a team logo to its corresponding sign.  Location refers to home/away. '''
    location = location.upper()

    sign_namespace = '{0}SIGN'.format(location)
    logo_namespace = '{0}LOGO'.format(location)

    sign_atch_board = None
    logo_atch_board = None

    # Get basic attachment points
    try:
        sign_atch_board  = pm.PyNode('{0}:ATTACH_01'.format(sign_namespace))
        sign_atch_bldg   = pm.PyNode('{0}:ATTACH_05'.format(sign_namespace))
        sign_atch_mascot = pm.PyNode('{0}:ATTACH_06'.format(sign_namespace))

        logo_atch_board  = pm.PyNode('{0}:ATTACH_01'.format(logo_namespace))

    except:
        pm.warning('Build Scene  ERROR Critical attachment points not found for {0} team.'.format(location))
    
    # Get optional attachment points.  These do not exist in every element.
    try:
        logo_atch_bldg   = pm.PyNode('{0}:ATTACH_05'.format(logo_namespace))
    except: logo_atch_bldg = None
    try:
        logo_atch_mascot = pm.PyNode('{0}:ATTACH_06'.format(logo_namespace))
    except: logo_atch_mascot = None

    if (sign_atch_board) and (logo_atch_board):
        attach(sign_atch_board, logo_atch_board)

    if (logo_atch_bldg):
        attach(sign_atch_bldg, logo_atch_bldg)
    if (logo_atch_mascot):
        attach(sign_atch_mascot, logo_atch_mascot)    
    return


def attachSignToScene(location):
    ''' Attaches a sign to its corresponding locator in the scene.  Location refers to home/away '''
    location = location.upper()

    sign_namespace = '{0}SIGN'.format(location)

    scene_loc = None
    sign_loc = None

    # Check for attachment locators
    try:
        scene_loc = pm.PyNode('{0}_LOCATOR'.format(location))
    except: 
        pm.warning('Build Scene  ERROR Missing sign attachment locator for {0} team.'.format(location))
        return

    try:
        sign_loc = pm.PyNode('{0}SIGN:MAIN_POS'.format(location))
    except:
        pm.warning('Build Scene  ERROR Could not find sign master control curve for {0} team.'.format(location))
        return

    if (scene_loc) and (sign_loc):
        attach(scene_loc, sign_loc)

    return


def attachRegion(location):
    ''' Attaches a region object to its corresponding locator in the scene.  Location refers to
        home/away '''
    location = location.upper()

    region_namespace = '{0}REGION'.format(location)

    scene_loc = None
    region_loc = None

    try:
        scene_loc = pm.PyNode('REGION_LOCATOR')
    except:
        pm.warning('Build Scene  ERROR Missing scene attachment locator for region.')
    
    try:
        region_loc = pm.PyNode('{0}REGION:MAIN_POS'.format(location))
    except:
        pm.warning('Build Scene  ERROR Missing region attchment locator.')

    if (scene_loc) and (region_loc):
        attach(scene_loc, region_loc)

    return


def attachLightRig(location):
    ''' Attaches a light rig to its corresponding home/away locator in the scene.'''
    location = location.upper()

    lgtrig_namespace = '{0}_ENV_LGT'.format(location)

    scene_loc = None
    lgtrig_loc = None

    try:
        scene_loc = pm.PyNode('{}_LOCATOR'.format(location))
    except:
        pm.warning('Build Scene  ERROR Missing scene attachment locator for {0} team'.format(location))

    try:
        lgtrig_loc = pm.PyNode('{}_ENV_LGT:MAIN_POS'.format(location))
    except:
        pm.warning('Build Scene  ERROR Missing attachment locator for light rig for {0} team'.format(location))

    if (scene_loc) and (lgtrig_loc):
        attach(scene_loc, lgtrig_loc)

    return


def attachLayout(project):
    ''' Attaches a layout to its corresponding locator in the scene. 
        NOTE:  THIS ALSO INCLUDES THE LAYOUT LIGHT RIG FOR CONVENIENCE  '''
    
    scene_loc = None
    layout_loc = None
    lgtrig_loc = None

    try:
        scene_loc = pm.PyNode('LAYOUT_LOCATOR')
    except:
        pm.warning('Build Scene  ERROR Missing scene attachment locator for layout.')

    try:
        layout_loc = pm.PyNode('{}_LAYOUT|RIG|MAIN_POS'.format(project))
        lgtrig_loc = pm.PyNode('LAYOUT_ENV_LGT:MAIN_POS')
    except:
        pm.warning('Build Scene  ERROR Missing layout attachment locator or layout light rig locator.')

    if (scene_loc) and (layout_loc) and (lgtrig_loc):
        attach(scene_loc, layout_loc)
        attach(scene_loc, lgtrig_loc)

    return


def attach(parent, child):
    ''' Combines parent and scale constraining into one command. '''
    pc = pm.parentConstraint(parent, child, mo=False)
    sc = pm.scaleConstraint(parent, child, mo=False)
    return (pc,sc)
