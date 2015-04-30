import os
import sys
from esky import bdist_esky
from distutils.core import setup

# from OpenGL.arrays import ctypes, logging
# import OpenGL.arrays.arraydatatype
# import OpenGL.arrays.ctypesparameters


def get_files(directory, destdir, files_list):
    files = []
    for f in os.listdir(directory):
        path = "{0}/{1}".format(directory, f)
        if os.path.isdir(path):
            get_files(path, "{0}/{1}".format(destdir, f), files_list)
        else:
            files.append(path)
    files_list.append((destdir, files))


def get_data_files(directory, destdir):
    all_files = []
    get_files(directory, destdir, all_files)
    return all_files


openglimports = [
    'OpenGL.arrays.ctypesparameters',
    'OpenGL.arrays._arrayconstants',
    'OpenGL.acceleratesupport',
    'OpenGL.arrays.arraydatatype',
    'OpenGL.arrays.numpymodule',
    'OpenGL.arrays.arrayhelpers',
    'OpenGL.arrays.buffers',
    'OpenGL.arrays.ctypesarrays',
    'OpenGL.arrays.ctypespointers',
    'OpenGL.arrays.formathandler',
    'OpenGL.arrays.lists',
    'OpenGL.arrays.nones',
    'OpenGL.arrays.numbers',
    'OpenGL.arrays.numpybuffers',
    'OpenGL.arrays.strings',
    'OpenGL.arrays.vbo',
#     'OpenGL.platform.baseplatform',
#     'OpenGL.platform.ctypesloader',
#     'OpenGL.platform.glx',
#     'OpenGL.platform.egl',
    'ctypes',
    'logging',
    'OpenGL_accelerate.arraydatatype',
    # 'OpenGL.arrays.numarrays',
    # 'OpenGL.arrays._numeric',
    # 'OpenGL.arrays._strings',
    # 'OpenGL.arrays.numeric',
    # 'OpenGL.arrays.numericnames',
    ]

# OpenGL hook
if os.name == 'nt':
    hiddenimports = ['OpenGL.platform.win32']
else:
    if sys.platform == 'linux2':
        hiddenimports = ['OpenGL.platform.glx']
    elif sys.platform[:6] == 'darwin':
        hiddenimports = ['OpenGL.platform.darwin']
    else:
        print 'ERROR: hook-OpenGL: Unrecognised combo (os.name: %s, sys.platform: %s)' % (os.name, sys.platform)

# lxml hook
hiddenimports += ['lxml._elementpath', 'gzip']

ESKY_OPTIONS = {
    "includes": [
        "PySide",
        "OpenGL",
        "numpy",
        "psutil",
        "raven",
        "raven.events",
        "raven.processors",
        "serial"] + hiddenimports + openglimports,
    }


IMAGES_PATH = "resources/images"
IMAGES = ["{0}/{1}".format(IMAGES_PATH, p) for p in \
            os.listdir(os.getcwd() + "/{0}".format(IMAGES_PATH))]

QML_PATH = "omni3dapp/gui/qml"
QML_FILES = get_data_files(QML_PATH, "omni3dapp/gui/qml")


setup(name="mak3r",
      version="0.1",
      description="Mak3r app",
      author="Omni 3D",
      author_email="annaw@omni3d.net",
      url="http://omni3d.net",
      packages=["omni3dapp",
          "omni3dapp/gui",
          "omni3dapp/gui/tools",
          "omni3dapp/gui/util",
          "omni3dapp/util",
          "omni3dapp/util/meshLoaders",
          "omni3dapp/util/printing",
          "omni3dapp/util/printing/power",
          ],
      package_data={"omni3dapp": ["version"]},
      scripts=["omniapp.py"],
      data_files = [
          (IMAGES_PATH, IMAGES),
          ("CuraEngine", ["CuraEngine/CuraEngine"])
          ] + QML_FILES,
      options=dict(bdist_esky=ESKY_OPTIONS),
     )
