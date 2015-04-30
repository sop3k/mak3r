# -*- coding: utf-8 -*-

import os
import sys
import inspect
from optparse import OptionParser

from PySide import QtGui
from OpenGL.arrays import *

from omni3dapp.util import profile
from omni3dapp.logger import log


if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    thisdir = os.path.dirname(inspect.getfile(inspect.currentframe()))
    BASE_DIR = os.path.abspath(thisdir)


def parse_arguments():
    parser = OptionParser(usage="usage: %prog [options] <filename>.stl")
    parser.add_option("-i", "--ini", action="store", type="string", dest="profileini",
        help="Load settings from a profile ini file")
    parser.add_option("-r", "--print", action="store", type="string", dest="printfile",
        help="Open the printing interface, instead of the normal cura interface.")
    parser.add_option("-p", "--profile", action="store", type="string", dest="profile",
        help="Internal option, do not use!")
    parser.add_option("-s", "--slice", action="store_true", dest="slice",
        help="Slice the given files instead of opening them in Cura")
    parser.add_option("-o", "--output", action="store", type="string", dest="output",
        help="path to write sliced file to")
    parser.add_option("--serialCommunication", action="store", type="string", dest="serialCommunication",
        help="Start commandline serial monitor")

    return parser.parse_args()


def setUp(app):
    """
    Main entry point. Parses arguments, and starts GUI or slicing process depending on the arguments.
    """
    (options, args) = parse_arguments()

    preference_path = profile.getPreferencePath()
    profile.loadPreferences(preference_path)

    if options.profile is not None:
        profile.setProfileFromString(options.profile)
    elif options.profileini is not None:
        profile.loadProfile(options.profileini)
    else:
        profile.loadProfile(profile.getDefaultProfilePath(), True)

    from omni3dapp.gui.app import OmniApp
    OmniApp(app, args)


if __name__ == "__main__":

    app = QtGui.QApplication(sys.argv)
    setUp(app)

    sys.exit(app.exec_())
