import nuke
from os import makedirs


def getAllNodesByType(typ=''):
    return_nodes = []

    if typ == '':
        return None

    for n in nuke.allNodes():
        if n.Class() == typ:
            return_nodes.append(n)

    return return_nodes


def checkForQT():
    read_nodes = getAllNodesByType('Read')
    qt_found = []

    for rn in read_nodes:
        read_path = rn['file'].getValue()
        if '.mov' in read_path:
            qt_found.append(rn)

    if len(qt_found):
        for rn in qt_found:
            print rn.name()
            rn.setSelected(True)
    else:
        print 'No quicktimes found!'
        return False


def makeFolders():

    wn = nuke.selectedNodes()[0]

    path = wn.knob('file').getValue()

    makedirs(path)


##########################################
# CFB-Specific crap
##########################################

SWAP_PATHS = {
    'R:/Projects/3013_ESPN_CFB_2015/04_Prod/ASSETS_LK/': 'Y:/Workspace/MASTER_PROJECTS/CFB_15/TOOLKIT/001_3D_ASSETS/',
    'R:/Projects/3013_ESPN_CFB_2015/04_Prod/ASSETS_ESPN/002_3D_Teams': 'Y:/Workspace/MASTER_PROJECTS/CFB_15/TOOLKIT/002_3D_TEAMS',
    'R:/Projects/3013_ESPN_CFB_2015/04_Prod/ASSETS_ESPN/001_3D_Assets': 'Y:/Workspace/MASTER_PROJECTS/CFB_15/TOOLKIT/001_3D_ASSETS',
    'R:/Projects/3013_ESPN_CFB_2015/04_Prod/ASSETS_ESPN/000_ANIMATION': 'Y:/Workspace/MASTER_PROJECTS/CFB_15/PROJECTS/000_ANIMATION',
    'R:/Projects/3013_ESPN_CFB_2015/04_Prod/ASSETS_LK/TEXTURES/MATTES/': 'Y:/Workspace/MASTER_PROJECTS/CFB_15/TOOLKIT/001_3D_ASSETS/TEXTURES/MATTES/',
    'R:/Projects/3013_ESPN_CFB_2015/04_Prod/ASSETS_LK/3D_ENV/': 'Y:/Workspace/MASTER_PROJECTS/CFB_15/TOOLKIT/001_3D_ASSETS/3D_ENV/',
    'CFP_E_NYS_ENDSTAMP_PLAYER_01': 'CFP_E_NYS_PLAYER_ENDSTAMP_01',
    'CFP_E_NYS_ENDSTAMP_TEAM_01': 'CFP_E_NYS_TEAM_ENDSTAMP_01',
    'CFP_E_NYS_ROLLOUT_FE_TEAM_01': 'CFP_E_NYS_TEAM_ROLLOUT_FE_01',
    'CFP_E_NYS_TEAM_MATCHUP_TRANS_01': 'CFP_E_NYS_MATCHUP_TRANS_01',
    'CFP_E_NYS_ENDSTAMP_MATCHUP_01': 'CFP_E_NYS_MATCHUP_ENDSTAMP_01',
    'CFP_E_CHAMP_PLAYER_TRANS_01': 'CFP_E_PLAYOFF_PLAYER_TRANS_01',
    'CFP_E_PLAYOFF_ENDSTAMP_PLAYER_01': 'CFP_E_PLAYOFF_PLAYER_ENDSTAMP_01',
    'CFP_E_PLAYOFF_ROLLOUT_FE_PLAYER_01': 'CFP_E_PLAYOFF_PLAYER_ROLLOUT_FE_01',
    'CFP_E_CHAMP_TEAM_TRANS_01': 'CFP_E_PLAYOFF_TEAM_TRANS_01',
    'CFP_E_PLAYOFF_ENDSTAMP_TEAM_01': 'CFP_E_PLAYOFF_TEAM_ENDSTAMP_01',
    'CFP_E_PLAYOFF_ROLLOUT_FE_TEAM_01': 'CFP_E_PLAYOFF_TEAM_ROLLOUT_FE_01',
    'CFP_E_PLAYOFF_TEAM_MATCHUP_TRANS_01': 'CFP_E_PLAYOFF_MATCHUP_TRANS_01',
    'CFP_E_CHAMP_ENDSTAMP_MATCHUP_01': 'CFP_E_PLAYOFF_MATCHUP_ENDSTAMP_01',
    'R:/Projects/14_009_ESPN_CFB/04_Prod/packages/CFP/CFP_E_CHAMP_REJOIN_MATCHUP_01/ren/work/maya/images': 'Y:/Workspace/MASTER_PROJECTS/CFB_15/PROJECTS/000_Animation/CFP_E_PLAYOFF_MATCHUjP_REJOIN_01/render_3d',
    'R:/Projects/14_009_ESPN_CFB/04_Prod/packages/CFP/CFP_E_PLAYOFF_REJOIN_MATCHUP_01/ren/work/maya/images': 'Y:/Workspace/MASTER_PROJECTS/CFB_15/PROJECTS/000_Animation/CFP_E_PLAYOFF_MATCHUP_REJOIN_01/render_3d',
    'R:/Projects/14_009_ESPN_CFB/04_Prod/packages/Base/Base_Logo_Artwork_for_Comp/bld/work/photoshop': 'Y:/Workspace/MASTER_PROJECTS/CFB_15/TOOLKIT/001_3D_ASSETS/Base/Base_Logo_Artwork_for_Comp/bld/work/photoshop',
    'R:/Projects/14_009_ESPN_CFB/04_Prod/packages/CFP/CFP_E_NYS_REJOIN_MATCHUP_01/ren/work/maya/images': 'Y:/Workspace/MASTER_PROJECTS/CFB_15/PROJECTS/000_Animation/CFP_E_NYS_MATCHUP_REJOIN_01/render_3d',
    'R:/Projects/14_009_ESPN_CFB/04_Prod/packages/CFP/CFP_E_NYS_B2B_MATCHUP_01/ren/work/maya/images': 'Y:/Workspace/MASTER_PROJECTS/CFB_15/PROJECTS/000_Animation/CFP_E_NYS_MATCHUP_B2B_01/render_3d',
    'R:/Projects/14_009_ESPN_CFB/04_Prod/packages/CFP/CFP_E_CHAMP_B2B_MATCHUP_01/ren/work/maya/images': 'Y:/Workspace/MASTER_PROJECTS/CFB_15/PROJECTS/000_Animation/CFP_E_PLAYOFF_MATCHUP_B2B_01/render_3d',
    '/Volumes/LK_RAID/Projects/14_009_ESPN_CFB/04_Prod/packages/CFP/CFP_E_NYS_ROLLOUT_FE_MATCHUP_01/ren/work/maya/images': 'Y:/Workspace/MASTER_PROJECTS/CFB_15/PROJECTS/000_Animation/CFP_E_NYS_MATCHUP_ROLLOUT_FE_01/render_3d',
    '/Volumes/LK_RAID/Projects/14_009_ESPN_CFB/04_Prod/packages/Base/Base_Logo_Artwork_for_Comp/bld/work/photoshop': 'Y:/Workspace/MASTER_PROJECTS/CFB_15/TOOLKIT/001_3D_ASSETS/Base/Base_Logo_Artwork_for_Comp/bld/work/photoshop',
    'R:/Projects/14_009_ESPN_CFB/04_Prod/packages/CFP/CFP_E_CHAMP_ROLLOUT_FE_MATCHUP_01/ren/work/maya/images': 'Y:/Workspace/MASTER_PROJECTS/CFB_15/PROJECTS/000_Animation/CFP_E_PLAYOFF_MATCHUP_ROLLOUT_FE_01/render_3d',
    'R:/Projects/14_009_ESPN_CFB/04_Prod/packages/CFP/CFP_E_CHAMP_ROLLOUT_FE_MATCHUP_01/ren/work/nuke/': 'Y:/Workspace/MASTER_PROJECTS/CFB_15/PROJECTS/000_Animation/CFP_E_PLAYOFF_MATCHUP_ROLLOUT_FE_01/render_2d/',
    '/Volumes/LK_RAID/Projects/14_009_ESPN_CFB/04_Prod/packages/CFP/CFP_E_NYS_TEAM_MATCHUP_TRANS_01/cmp/work/nuke/includes/': 'Y:/Workspace/MASTER_PROJECTS/CFB_15/PROJECTS/000_Animation/CFP_E_MATCHUP_TRANS_01/nuke/includes/',
    '/Volumes/LK_RAID/Projects/14_009_ESPN_CFB/04_Prod/packages/CFP/CFP_E_NYS_ROLLOUT_FE_MATCHUP_01/cmp/work/nuke/': 'Y:/Workspace/MASTER_PROJECTS/CFB_15/PROJECTS/000_Animation/CFP_E_NYS_MATCHUP_ROLLOUT_FE_01/nuke/',
    'R:/Projects/14_009_ESPN_CFB/04_Prod/packages/CFP/CFP_E_NYS_ROLLOUT_FE_MATCHUP_01/cmp/work/nuke/':  'Y:/Workspace/MASTER_PROJECTS/CFB_15/PROJECTS/000_Animation/CFP_E_NYS_MATCHUP_ROLLOUT_FE_01/nuke/',
    'R:/Projects/3013_ESPN_CFB_2015/04_Prod/ASSETS_LK/TEXTURES/MATTES/MP00-generic/': 'Y:/Workspace/MASTER_PROJECTS/CFB_15/TOOLKIT/001_3D_ASSETS/TEXTURES/MATTES/MP00-generic/'
    }


def remapReadNodes():
    read_nodes = getAllNodesByType('Read')

    for rn in read_nodes:
        read_path = rn['file'].getValue()


        for k,v in SWAP_PATHS.iteritems():
            if k in read_path:
                print read_path.replace(k,v)
                rn['file'].setValue(read_path.replace(k,v))


def remapCameraNodes():
    read_nodes = getAllNodesByType('Camera')

    for rn in read_nodes:
        read_path = rn['file'].getValue()

        print rn

        for k,v in SWAP_PATHS.iteritems():
            if k in read_path:
                print read_path.replace(k,v)
                rn['file'].setValue(read_path.replace(k,v))


def remapPrecompNodes():
    precomp_nodes = getAllNodesByType('Precomp')

    for pc in precomp_nodes:
        pc_path = pc['file'].getValue()

        for k,v in SWAP_PATHS.iteritems():
            if k in pc_path:
                print pc_path.replace(k,v)
                pc['file'].setValue(pc_path.replace(k,v))


def remapAlembicNodes():
    readgeo_nodes = getAllNodesByType('ReadGeo2')

    for rg in readgeo_nodes:
        rg_path = rg['file'].getValue()

        for k,v in SWAP_PATHS.iteritems():
            if k in rg_path:
                print rg_path.replace(k,v)
                rg['file'].setValue(rg_path.replace(k,v))



def printReport():
    report = ''

    read_nodes = getAllNodesByType('Read')
    for rn in read_nodes:
        report += (rn['file'].getValue() + '\n')

    abc_nodes = getAllNodesByType('ReadGeo2')
    for an in abc_nodes:
        report += (an['file'].getValue() + '\n')

    cam_nodes = getAllNodesByType('Camera')
    for cam in cam_nodes:
        report += (cam['file'].getValue() + '\n')

    print report