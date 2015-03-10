import os
from esky import bdist_esky
from distutils.core import setup


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
#     'OpenGL.arrays.numarrays',
    'OpenGL.arrays._numeric',
    'OpenGL.arrays._strings',
    'OpenGL.arrays.ctypespointers',
    'OpenGL.arrays.lists',
    'OpenGL.arrays.numbers',
    'OpenGL.arrays.numeric',
    'OpenGL.arrays.strings',
    'OpenGL.arrays.ctypesarrays',
    'OpenGL.arrays.nones',
    'OpenGL.arrays.numericnames',
    'OpenGL.arrays.numpymodule',
    'OpenGL.arrays.vbo',
    ]


ESKY_OPTIONS = {
    "includes": [
        "PySide",
        "OpenGL",
        "OpenGL.platform.glx",
        "numpy",
        "psutil",
        "serial"] + openglimports,
    }


IMAGES_PATH = "resources/images"
IMAGES = ["{0}/{1}".format(IMAGES_PATH, p) for p in \
            os.listdir(os.getcwd() + "/{0}".format(IMAGES_PATH))]

QML_PATH = "omni3dapp/gui/qml"
QML_FILES = get_data_files(QML_PATH, "qml")


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
          "omni3dapp/util/printing/power"
          ],
      package_data={"omni3dapp": ["version"]},
      scripts=["omniapp.py"],
      data_files = [
          (IMAGES_PATH, IMAGES),
          ("CuraEngine", ["CuraEngine/CuraEngine"])
          ] + QML_FILES,
      options=dict(bdist_esky=ESKY_OPTIONS),
     )
