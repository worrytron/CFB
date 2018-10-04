import nuke
import string
from os import mkdir
from os.path import exists
import yaml
import cfb

CSV_LOCATION = "\\\\cagenas\\workspace\\master_projects\\cfb_15\\toolkit\\098_misc\\text_transition_terms.csv"
SRC_PNG_FOLDER = "//cagenas/Workspace/MASTER_PROJECTS/CFB_15/PROJECTS/000_Animation/CFP_E_TEXT_TRANS/titles/"
OUTPUT_BASE_FOLDER = "//cagenas/Workspace/MASTER_PROJECTS/CFB_15/PROJECTS/000_Animation/CFP_E_TEXT_TRANS/render_2d/"
OUTPUT_SCRIPT_FOLDER = "//cagenas/Workspace/MASTER_PROJECTS/CFB_15/PROJECTS/000_Animation/CFP_E_TEXT_TRANS/nuke/renderfarm/"

OUTPUT_TEMP_FOLDER = "Temporary_Render_Folder/"
#OUTPUT_CHAMP_FOLDER = "CFP_E_Text_Trans_Champ/"
#OUTPUT_TEAM_FOLDER = "CFP_E_Text_Trans_"

MASTER_CTRL = nuke.toNode('MASTER_CTRL')
WRITE_DOT = nuke.toNode('write_dot')
WRITE_NODE = nuke.toNode('WriteScenes')

START = 1
END = 95

def generateOutputFolders(*a):
        
        terms_list = getTerms()
        
        # Make folders for all team tricodes
        yaml_stream = open(cfb.TEAM_DATABASE)
        db = yaml.load_all(yaml_stream)

        for team in db:
            folder = OUTPUT_BASE_FOLDER + '/TEAM/' + team['tricode'] + '/'
            if exists(folder):
                pass
            else:
                mkdir(folder)
                print "Created folder: " + folder

                # Make folders for all terms within each team folder              
            for t in terms_list:
                termFolder = folder + t + '/'
                if exists(termFolder):
                    pass
                else:
                    mkdir(termFolder)
                    print "Created folder: " + termFolder

        # Make folders for generic CFP and ESPN
        genericFolderCFP = OUTPUT_BASE_FOLDER + '/GENERIC_CFP/'
        genericFolderESPN = OUTPUT_BASE_FOLDER + '/GENERIC_ESPN/'

        for t in terms_list:
                termFolderCFP = genericFolderCFP + t + '/'
                termFolderESPN = genericFolderESPN + t + '/'
                if exists(termFolderCFP):
                        pass
                else:
                        mkdir(termFolderCFP)
                        print "Created folder: " + termFolderCFP
                if exists(termFolderESPN):
                        pass
                else:
                        mkdir(termFolderESPN)
                        print "Created folder: " + termFolderESPN

def generateSourceReads(*a):
    switch_node = nuke.nodes.Switch(name="INPUT_SWITCH")
    terms_list = getTerms()

    for i in range(len(terms_list)-1):
        read_node = nuke.nodes.Read()
        read_node.knob('file').setValue(SRC_PNG_FOLDER + terms_list[i] + ".png")
        switch_node.connectInput(i, read_node)

def generateWriteNodes(*a):
    terms_list = getTerms()

    #if MASTER_CTRL.knob('type').getValue() == 0:
    #    output_subtype = OUTPUT_GENERIC_FOLDER
    #elif MASTER_CTRL.knob('type').getValue() == 1:
    #    output_subtype = OUTPUT_CHAMP_FOLDER
    #elif MASTER_CTRL.knob('type').getValue() == 2:
    #    output_subtype = OUTPUT_TEAM_FOLDER + MASTER_CTRL.knob('teamTricode').getValue() + '/'

    for i in range(len(terms_list)-1):
        write_node = nuke.nodes.Write()
        write_node.knob('file').setValue(OUTPUT_BASE_FOLDER + OUTPUT_TEMP_FOLDER + terms_list[i] + '/' + terms_list[i] + '.#.png'  )
        write_node.knob('file_type').setValue('png')
        
        index_knob = nuke.Int_Knob("term_index", "Term Index")
        write_node.addKnob(index_knob)
        write_node.knob('term_index').setValue(i)

        write_node.connectInput(0, WRITE_DOT)

def cleanup( _str ):
    valid_chars = "_" + string.ascii_letters + string.digits
    _str = _str.replace(" ", "_")
    return ''.join(c for c in _str if c in valid_chars)

def getTerms(*a):
    terms_list = []
    with open(CSV_LOCATION) as csv:
        for line in csv:
            terms_list.append(cleanup(line))
        return terms_list

def generateScenes(_range=None):

    # Set output folder
    if (MASTER_CTRL.knob('type').getValue() == 0): # ESPN
        sceneFolder = 'GENERIC_ESPN'
        filePrefix = 'GENERIC_ESPN'
    elif (MASTER_CTRL.knob('type').getValue() == 1): # CFP
        sceneFolder = 'GENERIC_CFP'
        filePrefix = 'GENERIC_CFP'
    else: # TEAM
        # Check tricode
        tricode = MASTER_CTRL.knob('teamTricode').getValue()
        yaml_stream = open(cfb.TEAM_DATABASE)
        db = yaml.load_all(yaml_stream)
        tricodeExists = False
        for team in db:
            if (team['tricode'] == tricode):
                tricodeExists = True
                break
        if (not tricodeExists): 
            nuke.message(tricode + " is not a valid tricode.")
            return # Stop if it doesn't exist
    
    sceneFolder = 'TEAM' + '/' + tricode + '/'
    save_folder = OUTPUT_SCRIPT_FOLDER + '/' + tricode + '/'
    filePrefix = tricode

    # Ask if they're sure about this
    doit = nuke.ask("Generate scenes for " + filePrefix + "?")

    if (doit):
        origScriptName = nuke.root()['name'].value()
        terms_list = getTerms()
        INPUT_SWITCH = nuke.toNode("INPUT_SWITCH")

        if not _range:
            _range = range(len(terms_list))
        else:
            _range = range(_range[0], _range[1])

        if exists(save_folder):
            pass
        else:
            mkdir(save_folder)

        # Create scene for every term
        for i in _range:
            INPUT_SWITCH.knob('which').setValue(i)
            # Check that the output folder exists
            sequence_folder = OUTPUT_BASE_FOLDER + sceneFolder + '/' + terms_list[i] + '/'
            if exists(sequence_folder):
                pass
            else:
                mkdir(sequence_folder)
                print "Created folder: " + sequence_folder
            WRITE_NODE.knob('file').setValue(sequence_folder + terms_list[i] + r".%02d.png")
            nuke.scriptSaveAs( save_folder + filePrefix + '_' + terms_list[i] + '.nk', 1)

        # Resave as original name
        nuke.scriptSaveAs(origScriptName, 1)

def megaRender( _range ):
    terms_list = getTerms()
    write_nodes = findNodeType('Write')['Write']
    INPUT_SWITCH = nuke.toNode("INPUT_SWITCH")

    if not _range:
        _range = range(len(terms_list))
    else:
        _range = range(_range)
    #if generic:
    #    MASTER_CTRL.knob('type').setValue(0)
    #elif champ:
    #    MASTER_CTRL.knob('type').setValue(1)
    #elif team:
    #    MASTER_CTRL.knob('type').setValue(2)
    #    MASTER_CTRL.knob('team').setValue(teamName)
    
    for i in _range:
        INPUT_SWITCH.knob('which').setValue(i)

        active_write_node = None

        for wn in write_nodes:
            wn = nuke.toNode(wn)
            
            # Nuke returns an error instead of None when trying to get a nonexistent attribute
            try:
                write_index = wn.knob('term_index').getValue()
            except:
                continue
            
            # Since this is a valid scripted write node, check if it matches the index
            if write_index == i:
                break
            else:
                continue
        
        try:
            nuke.execute(wn, START, END, 1)
            print 'Successfully rendered: ' + terms_list[i]
        except RuntimeError:
            print 'Failed rendering: ' + terms_list[i]
            pass

#generateSourceReads()
def findNodeType(nodeList):
    """
    Stolen from: http://www.kurianos.com/wordpress/?p=574
    Small helper function for find the node type from nuke.
    :param nodeList: This should be a list
    :type nodeList: list
    :return: nodes and node type
    :rtype: dict
    Example
        >>> import find_node_type as fns
        >>> node_to_find = ["roto_a","write_b","shuffle_mode"]
        >>> node_found = fns.find_node_type(node_to_find)
        >>> print node_found
        >>> {'Roto': ['roto_a'], 'Write': ['write_b'], 'Shuffle':['shuffle_mode']}
    """
    #~ return var and this is dict type
    found_nodes = {}
    #~ getting all available nodes from the nuke scene file
    get_nuke_node_list = nuke.root().nodes()
    #~ looping throuh the list provided by user
    for each_node in nodeList:
        #~ loop throuh the nodes we found in the nuke scene file
        for each_nd in get_nuke_node_list:
            #~ getting node class type from node
            node_class = each_nd.Class()
            if each_nd.name().find(each_node) != -1:
                #~ if the node is there in the dict then add to the list
                #~ or create the key and add value
                if found_nodes.has_key(node_class):
                    found_nodes[node_class].append(each_nd.name())
                else:
                    found_nodes[node_class]=[]
                    found_nodes[node_class].append(each_nd.name())
    #~ return what we found from the scene
    return(found_nodes)
