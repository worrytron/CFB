from os import makedirs
import pymel.core as pm

SWAP_PATHS = {
    r"R:/Projects/14_009_ESPN_CFB/04_Prod/packages/Base/Base_FGRASS/bld/work/maya/includes": r"Y:/Workspace/MASTER_PROJECTS/CFB_15/TOOLKIT/001_3D_ASSETS/Base/Base_FGRASS/bld/work/maya/includes"
    }


def remapTextureNodes():
    file_nodes = pm.ls(typ='file')

    for fn in file_nodes:
        tex_path = fn.fileTextureName.get()

        print tex_path

        for k,v in SWAP_PATHS.iteritems():
            if k in tex_path:
                fn.fileTextureName.set(tex_path.replace(k,v))

def remapProxyNodes():
    proxy_nodes = pm.ls(typ='VRayMesh')

    for proxy in proxy_nodes:
        proxy_path = proxy.fileName.get()


        for k,v in SWAP_PATHS.iteritems():
            if k in proxy_path:
                print 'xx  ' + proxy_path
                print '>>  ' + proxy_path.replace(k,v)
                proxy.fileName.set(proxy_path.replace(k,v))

