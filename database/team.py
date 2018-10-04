import sys
#sys.path.append('f:/10_github/py-yaml-3.11/lib')
import yaml

from pipeline import cfb

## TEAM DATABASE OBJECT
class Team(object):
    def __init__(self, team_tricode):
        yaml_stream = open(cfb.TEAM_DATABASE)
        db = yaml.load_all(yaml_stream)
        found = 0
        
        # Converts matte painting index to its full name
        matte_conv = {
             0: 'MP00-generic',
             1: 'MP01-pacNW',
             2: 'MP02-noCal',
             3: 'MP03-soCal',
             4: 'MP04-soWest',
             5: 'MP05-rockies',
             6: 'MP06-texas',
             7: 'MP07-okla',
             8: 'MP08-gtLakes',
             9: 'MP09-centPlains',
             10: 'MP10-midWest',
             11: 'MP11-soEast',
             12: 'MP12-deepSouth',
             13: 'MP13-appalach',
             14: 'MP14-centEast',
             15: 'MP15-noEast',
             16: 'MP16-soFla'
        }
        
        #Converts sky index to full name
        sky_conv = {
            1: 'Sky1_generic',
            2: 'Sky2_pacNW',
            3: 'Sky3_texas',
            4: 'Sky4_midWest',
            5: 'Sky5_nightSky'
        }
        
        # Parse the db to find the team by tricode or name 
        for team in db:
            if (team['tricode'] == team_tricode) or (team['team'] == team_tricode):
                self.db = team
                found = 1
                break
        
        if not found:
            raise AttributeError('Team not found in database -- check your tricodes and try again.')

        else:    
            # Team info
            self.name     = team['team']
            self.nickname = team['mascot']
            self.safename = team['os_safe']
            self.tricode  = team['tricode']

            # Team categories
            self.conf     = self.db['conference']
            # Team internal information
            self.sign     = team['sign']
            self.signNum  = self.signToInt(self.sign)
            self.matte    = matte_conv[team['matte']]
            self.matteNum = int(team['matte'])
            self.sky      = sky_conv[team['sky']]
            self.skyNum   = int(team['sky'])-1
            self.switch   = False
            
            # Team colors
            self.primary  = (self.db['primary'][0], 
                             self.db['primary'][1], 
                             self.db['primary'][2]
                             )
            self.secondary = (self.db['secondary'][0], 
                              self.db['secondary'][1], 
                              self.db['secondary'][2]
                              )
            self.billboard = team['billboard']
            self.neon      = team['neon']
            
        yaml_stream.close()
    
    def __repr__(self):
        return '{0}\n{1} {2}'.format(self.tricode, self.name, self.nickname)

    def signToInt( self, signLetter, flip=False ):
        ''' Converts a sign letter into an index value. '''
        signNum = 0
        if 'A' in signLetter:
            signNum = 0
        if 'B' in signLetter:
            signNum = 1
        if 'C' in signLetter:
            signNum = 2
        if flip==True:
            signNum = signNum + 3
        return signNum

def getAllTeams( asNames=False, asDict=False ):
   with open(cfb.TEAM_DATABASE) as yaml_stream:
        stream = yaml.load_all(yaml_stream)
       
        if asNames:
           return [t['tricode'] for t in stream if t['tricode']]
        elif asDict:
           return [t for t in stream]

def checkTeams( team_list ):
    report = ''
    flag = 0
    for team in team_list:
        try:
            t = Team(team)
        except: 
            report += str(team) + ' '
            flag = 1

    if (flag):
        print '\n\nTricode  ERROR One or more tricodes not found. ({}) Stopping ... '.format(report.rstrip())
        return False

    else:
        return True