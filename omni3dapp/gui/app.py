# -*- coding: utf-8 -*-

import os
import sys
# import esky
import platform
import shutil
import glob
from urllib2 import URLError

from PySide import QtCore, QtGui, QtOpenGL

from mainwindow import MainWindow

from omni3dapp.logger import log
from omni3dapp.util import profile


YES_BTN = QtGui.QMessageBox.Yes
NO_BTN = QtGui.QMessageBox.No

UPDATES_URL = "http://omni3d.dev.neadoo.com/mak3r"


class OmniApp(object):

    def __init__(self, app, files):
        self.main_window = None
        self.splash = None
        self.load_files = files

        if sys.platform.startswith('darwin'):
            # Do not show a splashscreen on OSX, as by Apple guidelines
            self.after_splash()
        else:
            self.set_splash_screen()
            self.splash.show()
            app.processEvents()
            self.after_splash()

        gl_format = QtOpenGL.QGLFormat()
        gl_format.setSampleBuffers(True)
        gl_widget = QtOpenGL.QGLWidget(gl_format)

        self.main_window = MainWindow()
        self.main_window.setViewport(gl_widget)
        self.main_window.setViewportUpdateMode(
            QtGui.QGraphicsView.FullViewportUpdate)

        self.splash.finish(self.main_window)
        self.main_window.showMaximized()

        # if profile.getPreference('check_for_updates') == 'True' and \
        #         hasattr(sys, 'frozen'):
        #     try:
        #         self.check_for_updates()
        #     except Exception as e:
        #         log.error("Something went wrong while fetching updates: "
        #                   "{0}".format(e))

    def set_splash_screen(self):
        from omni3dapp.util.resources import getPathForImage
        pixmap = QtGui.QPixmap(getPathForImage('splashimage.png'))
        self.splash = QtGui.QSplashScreen(
            pixmap, QtCore.Qt.WindowStaysOnTopHint)

    def get_executable(self):
        executable = sys.executable
        if platform.system() == "Windows":
            # Find correct executable
            appdir = os.path.dirname(sys.executable)
            from esky.bootstrap import split_app_version, is_version_dir, \
                pathjoin
            for nm in os.listdir(appdir):
                (appnm, ver, platform_name) = split_app_version(nm)
                if not (ver and platform_name):
                    continue
                if is_version_dir(pathjoin(appdir, nm)):
                    executable = pathjoin(appdir, nm,
                                          sys.executable.split("\\")[-1])
        return executable

    def check_for_updates(self):
        executable = self.get_executable()
        try:
            eskyapp = esky.Esky(executable, UPDATES_URL)
        except esky.errors.EskyBrokenError as e:
            log.error("Esky error: {0}".format(e))
            return
        try:
            newver = eskyapp.find_update()
        except URLError:
            log.error("Could not connect to updates server.")
        else:
            if newver is not None:
                update_dialog = QtGui.QMessageBox.question(
                    self.main_window,
                    _("Update application?"),
                    _("New version is available. Do you wish to update the "
                      "application?"),
                    YES_BTN | NO_BTN,
                    YES_BTN
                    )

                if update_dialog == YES_BTN:
                    eskyapp.fetch_version(newver)
                    # TODO: Show progress bar while installing
                    # (or relevant message)
                    eskyapp.install_version(newver)

                    QtGui.QMessageBox.information(
                        self.main_window,
                        _("Update complete"),
                        _("Application updated from version {0} to version"
                          " {1}.\nYou should restart the application now"
                          " to apply changes".format(eskyapp.version, newver))
                        )

        eskyapp.cleanup()

    def after_splash(self):
        from omni3dapp.util import resources, profile
        resources.setupLocalization(profile.getPreference('language'))

        # If we do not have preferences yet,
        # try to load it from a previous app install
        if profile.getMachineSetting('machine_type') == 'unknown':
            try:
                otherCuraInstalls = profile.getAlternativeBasePaths()
                otherCuraInstalls.sort()
                if len(otherCuraInstalls) > 0:
                    profile.loadPreferences(os.path.join(
                        otherCuraInstalls[-1], 'preferences.ini'))
                    profile.loadProfile(os.path.join(
                        otherCuraInstalls[-1], 'current_profile.ini'))
            except Exception, e:
                import traceback
                print traceback.print_exc()
                log.error(e)
