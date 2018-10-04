##############################################################################
###                  PROJECT-SPECIFIC GLOBAL VARIABLES:                    ###
###            COLLEGE FOOTBALL 2015 PLAYOFFS / REGULAR SEASON             ###
##############################################################################

# 04/22/15

# Main project directory
PROJECT_BASE_DIR = "Y:\\Workspace\\MASTER_PROJECTS\\CFB_15\\"

# Asset directories
MAIN_ASSET_DIR = PROJECT_BASE_DIR + "TOOLKIT\\001_3D_ASSETS\\"
TEAMS_ASSET_DIR = PROJECT_BASE_DIR + "TOOLKIT\\002_3D_TEAMS\\"
ANIMATION_PROJECT_DIR = PROJECT_BASE_DIR + "PROJECTS\\000_Animation\\"

# LK-specific asset directories
LK_ASSET_DIR = PROJECT_BASE_DIR + "ASSETS_LK\\"
LK_ANIMATION_PROJECT_DIR = PROJECT_BASE_DIR + "MASTER\\"

# Database locations
TEAM_DATABASE = PROJECT_BASE_DIR + "TOOLKIT\\097_SCRIPTS\\pipeline\\database\\cfb_teams.yaml"
SORTING_DATABASE = PROJECT_BASE_DIR + "TOOLKIT\\097_SCRIPTS\\pipeline\\database\\cfb_sorting.yaml"
#SORTING_DATABASE = "V:\\dev\\pipeline\\database\\cfb_sorting.yaml"
TEMPLATES_DATABASE = PROJECT_BASE_DIR + "TOOLKIT\\097_SCRIPTS\\pipeline\\database\\cfb_templates.yaml"

# Factory location
FACTORY_LIGHT_RIG = MAIN_ASSET_DIR + "\\000_FACTORY\\FACTORY.mb"

# Location for a default workspace.mel file
DEFAULT_WORKSPACE_MEL = "\\\\cagenas\\workspace\\scripts\\maya\\workspace.mel"

# Folder structure
FOLDER_STRUCTURE = {
        'ae': [],
        'mari': [],
        'maya': ['scenes', 'backup', 'atom'],
        'nuke': [],
        'c4d': [],
        'render_3d': [],
        'render_2d': ['prerenders'],
        'qt': [],
        'abc': [],
        'cam': []
        }


NAMESPACES = [
        'CFB_LOGO',
        'HOMELOGO',
        'AWAYLOGO',
        'HOMESIGN',
        'AWAYSIGN',
        'HOMEREGION',
        'AWAYREGION',
        'LAYOUT',
        'CAM',
        'CLOTH',
        'FACTORY'
        ]


FRAMEBUFFERS = {
    'beauty':[
        'reflection',
        'refraction',
        'specular',
        'diffuse',
        'SSS',
        'lighting',
        'selfIllum',
        'GI',
        'totalLight',
        'shadow'
        ],
    'utility':[
        'zDepth',
        'normals',
        'bumpNormals',
        'UV',
        'AO',
        'PPW',
        'MV',
        'facingRatio'
        ],
    'matte':['']
    }