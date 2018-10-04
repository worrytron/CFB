import json
import nuke
import os.path

DATABASE_PATH = "Y:\\Workspace\\SCRIPTS\\pipeline\\database"
PROJECT_PATH  = "Y:\\Workspace\\MASTER_PROJECTS\\NBA_2016\\001_PROJECTS\\000_Animation\\NBA_ES_PLAYER_TRANS_01"
NUKE_PATH     = os.path.join(PROJECT_PATH, 'nuke')
RENDER_PATH   = os.path.join(PROJECT_PATH, 'render_2d')


SWATCHES = {
    'primary': nuke.toNode('PRI'),
    'secondary': nuke.toNode('SEC'),
    'tertiary': nuke.toNode('TRI'),
    '3d_logo': nuke.toNode('LOGO_3D'),
    '2d_logo': nuke.toNode('LOGO_2D'),
    'wordmark': nuke.toNode('LOGO_WORDMARK'),
    'ticker': nuke.toNode('TICKER'),
    'typography': nuke.toNode('TYPOGRAPHY')
}

# GETTERS ##########################################################################################
def getProduction(prod_):
    ''' Gets a production's global variables from the database. '''
    PRODUCTION_GLOBALS_DB = os.path.join(DATABASE_PATH, "productions_db.json")
    merged_prod = {}
    with open(PRODUCTION_GLOBALS_DB, 'r') as stream:
        full_db = json.load(stream)
        for k,v in full_db.iteritems():
            # default project is stored
            if (k == 'DEFAULT'):
                default_prod = full_db[k]
            # a specific project is requested
            elif (k == prod_):
                request_prod = full_db[k]
                request_prod['is_default'] = False

            else: request_prod = {'is_default': True}
    # The project dictionaries only store the delta of data in the default dictionary
    # Therefore we merge the requested project dictionary over top of the default to create
    # a complete data set.
    merged_prod = default_prod.copy()
    merged_prod.update(request_prod)
    return merged_prod


def getTeamDatabase(prod_):
    ''' Gets the team database for a production. '''
    prod_db  = getProduction(prod_)
    if (prod_db['is_default'] == True):
        raise error.DatabaseError(1)

    team_db_ = prod_db['team_db']
    db_path  = os.path.join(DATABASE_PATH, '{0}.json'.format(team_db_))

    with open(db_path, 'r') as stream:
        full_db = json.load(stream)

    return full_db

def getTeam(prod_, tricode):
    ''' Gets a team from a production, based on tricode or full name.'''
    team_db = getTeamDatabase(prod_)
    for k,v in team_db.iteritems():
        if k == tricode:
            return team_db[k]
        elif ('{0} {1}'.format(team_db[k]['city'], team_db[k]['nick']) == tricode):
            return team_db[k]
    # if it gets this far, the team wasn't found in the database.
    raise error.DatabaseError(2)

def getAllTeams(prod_, name='tricode'):
    ''' Gets a list of all teams for a given production. '''
    team_db = getTeamDatabase(prod_)
    team_ls = []
    if name == 'tricode':
        for k in team_db:
            team_ls.append(k)
        return sorted(team_ls)
    elif name == 'full':
        for k,v in team_db.iteritems():
            team_ls.append('{0} {1}'.format(team_db[k]['city'], team_db[k]['nick']))
        return sorted(team_ls)
    elif name == 'city':
        for k,v in team_db.iteritems():
            team_ls.append('{0}'.format(team_db[k]['city']))
        return sorted(team_ls)
    elif name == 'nick':
        for k,v in team_db.iteritems():
            team_ls.append('{0}'.format(team_db[k]['nick']))
        return sorted(team_ls)

def getTeamColors(prod_, tricode):
    team = getTeam(prod_, tricode)
    ret_colors = {
        'primary': convertColor(team['primary']),
        'secondary': convertColor(team['secondary']),
        'tertiary': convertColor(team['tertiary'])
        }
    return ret_colors

def convertColor(colorvec, to='float'):
    ''' Converts a color vector from 0-255 (int) to 0-1 (float) or back again. '''
    def _clamp(value):
        if value < 0: return 0
        if value > 255: return 255
    if (to == 'float'):
        r_ = (1.0/255) * colorvec[0]
        g_ = (1.0/255) * colorvec[1]
        b_ = (1.0/255) * colorvec[2]
        return (r_, g_, b_, 1)
    if (to == 'int'):
        r_ = _clamp(int(255 * colorvec[0]))
        g_ = _clamp(int(255 * colorvec[1]))
        b_ = _clamp(int(255 * colorvec[2]))
        return (r_, g_, b_, 1)

def applyTeam():

    this_node = nuke.toNode('MASTER_CTRL')
    write_node= nuke.toNode('MASTER_WRITE')
    tricode = this_node.knob('tricode').getValue()
    if tricode == '':
        return

    colors = getTeamColors('NBA_2016', tricode)

    SWATCHES['primary'].knob('color').setValue(colors['primary'])
    SWATCHES['secondary'].knob('color').setValue(colors['secondary'])
    SWATCHES['tertiary'].knob('color').setValue(colors['tertiary'])

    logo_path_3d = r"Y:/Workspace/MASTER_PROJECTS/NBA_2016/004_TOOLBOX/005_IMS_UPLOADS/LOGOS/1024/NBA_Teams/{0}/{0}_3D.png".format(tricode)
    logo_path_2d = r"Y:/Workspace/MASTER_PROJECTS/NBA_2016/004_TOOLBOX/005_IMS_UPLOADS/LOGOS/1024/NBA_Teams/{0}/{0}.png".format(tricode)
    logo_path_wm = r"Y:/Workspace/MASTER_PROJECTS/NBA_2016/004_TOOLBOX/005_IMS_UPLOADS/LOGOS/1024/NBA_Teams/{0}/{0}_WORDMARK.png".format(tricode)
    ticker_path  = r"Y:/Workspace/MASTER_PROJECTS/NBA_2016/004_TOOLBOX/002_3D_TEAMS/{0}/tex/{0}_ticker_02.png".format(tricode)
    typography   = r"Y:/Workspace/MASTER_PROJECTS/NBA_2016/004_TOOLBOX/002_3D_TEAMS/{0}/tex/{0}_typography.png".format(tricode)

    SWATCHES['3d_logo'].knob('file').setValue(logo_path_3d)
    SWATCHES['2d_logo'].knob('file').setValue(logo_path_2d)
    SWATCHES['wordmark'].knob('file').setValue(logo_path_wm)
    SWATCHES['ticker'].knob('file').setValue(ticker_path)
    SWATCHES['typography'].knob('file').setValue(typography)

    write_node.knob('file').setValue(str(os.path.join(RENDER_PATH, tricode, "PLAYER_TRANS_BASE_{0}.#.png".format(tricode))).replace("\\","/"))
    nuke.scriptSaveAs('{0}/{1}.nk'.format(NUKE_PATH, tricode))

applyTeam()