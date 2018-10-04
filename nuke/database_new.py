import json
import os.path

DELIVERABLE        = "NBA_E_REG_SOT"
nuke_folder        = "Y:/Workspace/MASTER_PROJECTS/NBA_2016/001_PROJECTS/000_Animation/{}/nuke/TEAMS/".format(DELIVERABLE)
deliverable_folder = ["Y:/Workspace/MASTER_PROJECTS/NBA_2016/001_PROJECTS/000_Animation/{}/render_2d".format(DELIVERABLE), "", ""]
team_list          = []
left_rn            = nuke.toNode('READ_LEFT')
right_rn           = nuke.toNode('READ_RIGHT')
left_sec_rn        = nuke.toNode('READ_LEFT_SECONDARY')
right_sec_rn       = nuke.toNode('READ_RIGHT_SECONDARY')
write              = nuke.toNode('MASTER_WRITE')


with open("Y:\\Workspace\\SCRIPTS\\pipeline\\database\\teams_nba.json", 'r') as stream:
    db = json.load(stream)

for k in db:
    team_list.append(k)

for team in sorted(team_list):
	deliverable_folder[1] = "{}".format(team)
	deliverable_folder[2] = "{}_{}.#.png".format(DELIVERABLE, team)

    left_render = r"Y:/Workspace/MASTER_PROJECTS/NBA_2016/001_PROJECTS/000_Animation/NBA_E_REG_SOT/render_3d/{0}/v001/Main_passes/{0}_Main.%04d.exr".format(team)
    right_render = r"Y:/Workspace/MASTER_PROJECTS/NBA_2016/001_PROJECTS/000_Animation/NBA_E_REG_SOT/render_3d/{0}_RIGHT/v001/Main_passes/{0}_RIGHT_Main.%04d.exr".format(team)
    sec_logo = r"Y:/Workspace/MASTER_PROJECTS/NBA_2016/004_TOOLBOX/002_3D_TEAMS/{0}/tex/{0}_secondary.png".format(team)
    

	if not os.path.isdir(deliverable_folder[0] + '/' + deliverable_folder[1]):
		os.mkdir(deliverable_folder[0] + '/' + deliverable_folder[1])

    left_rn.knob('file').setValue(left_render)
    right_rn.knob('file').setValue(right_render)
    left_sec_rn.knob('file').setValue(sec_logo)
    right_sec_rn.knob('file').setValue(sec_logo)
    write.knob('file').setValue('/'.join(deliverable_folder))
    nuke.scriptSaveAs(os.path.join(nuke_folder, '{}.nk'.format(team)), overwrite=True)
