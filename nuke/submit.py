import nuke
import nukescripts
from os import listdir, getcwd
from os.path import isfile, join, basename, isdir
import subprocess
import time
import sys

#WRITE_NODE_NAME = "WriteScenes"
#frame_range = "1-300"
THREADS = 16
G_CLUSTER = '/C'

class QubeSubmitWindow(nukescripts.PythonPanel):
    def __init__(self):
        nukescripts.PythonPanel.__init__(self, "Submit to Qube", "ID")
        
        self.name = nuke.String_Knob('job_name', 'Job Name', basename(nuke.root().name()))
        self.addKnob(self.name)

        wn_ = []
        wn = nuke.selectedNodes()
        if wn == []:
            wn_str = ''
        else:
            for n in wn:
                if not n.Class() == 'Write':
                    wn.remove(n)
                else: wn_.append(n.name())
            wn_str = ','.join(wn_)

        self.path = nuke.Text_Knob('path', 'Scene Path:', '{} {}'.format(nuke.root().name(), wn_str))
        self.addKnob(self.path)

        self.writeNode = nuke.String_Knob('write_node', 'Write Node:', wn_str)
        self.addKnob(self.writeNode)

        self.frange = nuke.String_Knob('frange', 'Frame Range:', '{}-{}'.format(nuke.root().firstFrame(), nuke.root().lastFrame()))
        self.addKnob(self.frange)

        self.cluster = nuke.String_Knob('cluster', 'Cluster:', '/')
        self.addKnob(self.cluster)

        self.restrictions = nuke.String_Knob('restrictions', 'Restrictions (optional):', '')
        self.addKnob(self.restrictions)

        self.priority = nuke.String_Knob('priority', 'Priority:', '5000')
        self.addKnob(self.priority)

    def showModalDialog(self):
        ok = nukescripts.PythonPanel.showModalDialog(self)
        if ok:
            self.submit()

    def submit(self):
        if (self.frange.getValue() == '' or\
            self.priority.getValue() == '' or\
            self.writeNode.getValue() == ''):

            nuke.message('Required fields were not filled out.')
            self.showModalDialog()
            return

        write_nodes = self.writeNode.getValue().split(',')
        
        for wn in write_nodes:
            self.package = generatePackagePY(
                self.name.getValue() + ' ' + wn, 
                nuke.root().name(), 
                self.frange.getValue(), 
                self.priority.getValue(), 
                wn, 
                cluster=self.cluster.getValue()
                )
            subprocess.Popen(['c:\\program files (x86)\\pfx\\qube\\bin\\qube-console.exe', '--nogui', '--submitDict', str(self.package)])

def newSubmit():
    QubeSubmitWindow().showModalDialog()


#cmdline version
def generatePackage(job_name, script, frange, priority, cpus, write_node=''):
    submit_dict = {
        'prototype'    : 'cmdrange',
        'name'         : job_name,
        'priority'     : str(priority),
        'cpus'         : '1',
        'groups'       : 'Nuke',
        'reservations' : 'host.processors={}'.format(cpus),
        'package'      : {
            'simpleCmdType'    : 'Nuke (cmdline)',
            'executable'       : "C:\\Program Files\\Nuke8.0v6\\nuke8.0.exe",
            'script'           : str(script),
            'executeNodes'     : write_node,
            'range'            : frange,
            '-m'               : str(cpus),
            'minOpenSlots'     : cpus,
            'renderThreadCount': cpus,
            'nukeVersion'      : [str(nuke.NUKE_VERSION_MAJOR), str(nuke.NUKE_VERSION_MINOR), str(nuke.NUKE_VERSION_RELEASE), None]
            }
        }

    return submit_dict

# pyNuke version

def generatePackagePY(job_name, script, frange, priority, write_node='', cluster=G_CLUSTER):
    NUKE_EXE = {
        8:  "C:\\Program Files\\Nuke11.0v1\\Nuke11.0.exe",
        10: "C:\\Program Files\\Nuke11.0v1\\Nuke11.0.exe",
        11: "C:\\Program Files\\Nuke11.0v1\\Nuke11.0.exe"
        }

    submit_dict = {
        'prototype': 'pyNuke',
        'name'     : job_name,
        'priority' : str(priority),
        'cpus'     : '10',
        'groups'   : 'Nuke',
        'cluster'  : cluster,
        'restrictions': '',
        'reservations': 'host.processors={}'.format(THREADS),
        'package'  : {
            'pyExecutable' : NUKE_EXE[nuke.NUKE_VERSION_MAJOR],
            'scriptPath'   : script.replace('\\','/'),
            'executeNodes' : write_node,
            'range'        : frange,
            '-m'           : THREADS,
            'specificThreadCount': THREADS,
            'nukeVersion'  : [str(nuke.NUKE_VERSION_MAJOR), str(nuke.NUKE_VERSION_MINOR), str(nuke.NUKE_VERSION_RELEASE), None]
            }
        }

    return submit_dict


def singleNode(job_name, script, frange, priority, write_node):
    submit_dict = generatePackagePY(job_name, script, frange, priority, write_node)
    subprocess.Popen(['c:\\program files (x86)\\pfx\\qube\\bin\\qube-console.exe', '--nogui', '--submitDict', str(submit_dict)])
    time.sleep(3)


def folder(frame_range, write_node, nuke_file_path=None, prog_minmax=None, *a):
    if not nuke_file_path:
        nuke_file_path = raw_input('Enter the folder to parse: ')
    #start_frame = raw_input('Enter start frame: ')
    #end_frame = raw_input('Enter end frame: ')
    #frame_range = str(start_frame +"-"+ end_frame)

    nuke_files = [ (nuke_file_path + '\\' + f) for f in listdir(nuke_file_path) if isfile(join(nuke_file_path,f)) and ".nk" in f and not ".nk~" in f]
    #nk = nuke_files[0]
    progress_max = len(nuke_files)

    for i in range(progress_max):
        print "\n\n"
        print "SUBMITTING JOB ::: " + str(i+1) + " of " + str(progress_max+1)
        if prog_minmax:
            print "FROM FOLDER    ::: " + str(prog_minmax[0]+1) + " of " + str(prog_minmax[1]+1)
        print "\n\n"
        package = generatePackagePY(str(basename(nuke_files[i])), nuke_files[i], frame_range, 9999, cpus, write_node)
        subprocess.Popen(['c:\\program files (x86)\\pfx\\qube\\bin\\qube-console.exe', '--nogui', '--submitDict', str(package)])
        time.sleep(3)


def allFolders(base_folder=None, *a):
    if not folder:
        return None

    all_folders = [d for d in listdir(base_folder) if isdir(base_folder + d)]
    #progress_max = len(all_folders)
    progress_max = 4
    for i in range(progress_max):
        #print all_folders[i]
        prog = (i, progress_max)
        folder((base_folder + all_folders[i]), prog)


if __name__ == '__main__':
    frame_range = sys.argv[1]
    write_node = sys.argv[2]
    folder(frame_range, write_node, getcwd())
