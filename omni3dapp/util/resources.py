"""
Helper module to get easy access to the path where resources are stored.
This is because the resource location is depended on the packaging method and OS
"""
__copyright__ = "Copyright (C) 2013 David Braam - Released under terms of the AGPLv3 License"

import os
import sys
import glob
import platform

import gettext

if sys.platform.startswith('darwin'):
    try:
        #Foundation import can crash on some MacOS installs
        from Foundation import *
    except:
        pass

if sys.platform.startswith('darwin'):
    if hasattr(sys, 'frozen'):
        try:
            resourceBasePath = NSBundle.mainBundle().resourcePath()
        except:
            resourceBasePath = os.path.join(os.path.dirname(__file__), "../../../../../")
    else:
        resourceBasePath = os.path.join(os.path.dirname(__file__), "../../resources")
else:
    resourceBasePath = os.path.join(os.path.dirname(__file__), "../../resources")

def getPathForResource(direc, subdir, resource_name):
    assert os.path.isdir(direc), "{p} is not a directory".format(p=direc)
    path = os.path.normpath(os.path.join(direc, subdir, resource_name))
    assert os.path.isfile(path), "{p} is not a file.".format(p=path)
    return path

def getPathForImage(name):
    return getPathForResource(resourceBasePath, 'images', name)

def getDefaultMachineProfiles():
    path = os.path.normpath(os.path.join(resourceBasePath, 'machine_profiles', '*.ini'))
    return glob.glob(path)

def setupLocalization(selectedLanguage=None):
    # Defaults to english
    languages = ['en']

    if selectedLanguage is not None:
        for item in getLanguageOptions():
            if item[1] == selectedLanguage and item[0] is not None:
                languages = [item[0]]

    locale_path = os.path.normpath(os.path.join(resourceBasePath, 'locale'))
    translation = gettext.translation('Cura', locale_path, languages, fallback=True)
    translation.install(unicode=True)

def getLanguageOptions():
    return [
        ['en', 'English'],
        # ['de', 'Deutsch'],
        # ['fr', 'French'],
        # ['nl', 'Nederlands'],
        # ['es', 'Spanish'],
        # ['po', 'Polish']
    ]
