# -*- coding: utf-8 -*-

import os
import sys
import esky
import platform
import shutil
import glob
from urllib2 import URLError

from PySide import QtCore, QtGui

from mainwindow import MainWindow
from omni3dapp.logger import log

YES_BTN = QtGui.QMessageBox.Yes
NO_BTN = QtGui.QMessageBox.No

UPDATES_URL = "http://localhost:8080"


class OmniApp(object):

    def __init__(self, files):
        # TODO: check out and redirect stdout in Qt
        # if platform.system() == "Windows" and not 'PYCHARM_HOSTED' in os.environ:
        #     super(CuraApp, self).__init__(redirect=True, filename='output.txt')
        # else:
        #     super(CuraApp, self).__init__(redirect=False)
        app = QtGui.QApplication(sys.argv)

        self.main_window = None
        self.splash = None
        self.load_files = files

        if sys.platform.startswith('win'):
            # Check for an already running instance,
            # if another instance is running load files in there
            from omni3dapp.util import version
            from ctypes import windll
            import ctypes
            import socket
            import threading

            portNr = 0xCA00 + sum(map(ord, version.getVersion(False)))
            if len(files) > 0:
                try:
                    other_hwnd = windll.user32.FindWindowA(
                        None, ctypes.c_char_p('Omni 3D App - ' +
                                              version.getVersion()))
                    if other_hwnd != 0:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        sock.sendto('\0'.join(files), ("127.0.0.1", portNr))

                        windll.user32.SetForegroundWindow(other_hwnd)
                        return
                except:
                    log.error("Error loading files into already running \
                            application")

            socketListener = threading.Thread(target=self.Win32SocketListener,
                                              args=(portNr,))
            socketListener.daemon = True
            socketListener.start()
        elif sys.platform.startswith('darwin'):
            # Do not show a splashscreen on OSX, as by Apple guidelines
            self.after_splash()
        else:
            self.set_splash_screen()
            self.splash.show()
            app.processEvents()
            self.after_splash()
        self.main_window = MainWindow()
        self.splash.finish(self.main_window)
        self.main_window.show()

        if hasattr(sys, 'frozen'):
            self.check_for_updates()

        sys.exit(app.exec_())

    def set_splash_screen(self):
        from omni3dapp.util.resources import getPathForImage
        pixmap = QtGui.QPixmap(getPathForImage('splashimage.png'))
        self.splash = QtGui.QSplashScreen(pixmap, QtCore.Qt.WindowStaysOnTopHint)

    def run_config_wizard(self, resource_base_path):
        if platform.system() == "Windows":
            exampleFile = os.path.normpath(os.path.join(
                resource_base_path, 'example', 'UltimakerRobot_support.stl'))
        else:
            # Check if we need to copy our examples
            exampleFile = os.path.expanduser(
                '~/CuraExamples/UltimakerRobot_support.stl')
            if not os.path.isfile(exampleFile):
                try:
                    os.makedirs(os.path.dirname(exampleFile))
                except Exception, e:
                    log.error(e)
                for filename in glob.glob(os.path.normpath(os.path.join(
                        resource_base_path, 'example', '*.*'))):
                    shutil.copy(filename, os.path.join(os.path.dirname(
                        exampleFile), os.path.basename(filename)))
        self.loadFiles = [exampleFile]
        if self.splash is not None:
            self.splash.finish()
        # configWizard.configWizard()

    def check_for_updates(self):
        eskyapp = esky.Esky(sys.executable, UPDATES_URL)
        try:
            newver = eskyapp.find_update()
        except URLError:
            log.error("Could not connect to updates server.")
        else:
            if newver is not None:
                update_dialog = QtGui.QMessageBox.question(
                            self.main_window,
                            _("Update application?"),
                            _("New version is available. Do you wish to update the "\
                            "application?"),
                            YES_BTN | NO_BTN,
                            YES_BTN
                            )

                if update_dialog == YES_BTN:
                    eskyapp.fetch_version(newver)
                    # TODO: Show progress bar while installing (or relevant message)
                    eskyapp.install_version(newver)

                    QtGui.QMessageBox.information(
                            self.main_window,
                            _("Update complete"),
                            _("Application updated from version {0} to version"\
                            " {1}.\nYou should restart the application now"\
                            " to apply changes".format(eskyapp.version, newver))
                            )

                    # restart_dialog = QtGui.QDialog(self.main_window)
                    # restart_dialog.setWindowTitle("Update complete")

                    # yes_button = QtGui.QPushButton("Yes")
                    # yes_button.clicked.connect(self.restart)

                    # no_button = QtGui.QPushButton("No")
                    # no_button.clicked.connect(restart_dialog.close)

                    # label = QtGui.QLabel("Application updated from version {0} to version"\
                    #                 " {1}.\nDo you want to restart the application now"\
                    #                 " and apply changes?".format(eskyapp.version, newver))

                    # dialog_layout = QtGui.QVBoxLayout()
                    # dialog_layout.addWidget(label)
                    # dialog_layout.addWidget(yes_button)
                    # dialog_layout.addWidget(no_button)

                    # restart_dialog.setLayout(dialog_layout)
                    # restart_dialog.show()

        eskyapp.cleanup()

    def after_splash(self):
        from omni3dapp.util import resources, profile, version
        resources.setupLocalization(profile.getPreference('language'))

        # If we do not have preferences yet,
        # try to load it from a previous Cura install
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

        # If we haven't run it before, run the configuration wizard.
        # if profile.getMachineSetting('machine_type') == 'unknown':
        #     self.run_config_wizard(resources.resourceBasePath)

        # if profile.getPreference('check_for_updates') == 'True':
        #     res = self.check_for_updates(version.checkForNewerVersion())
        #     if res:
        #         return

        if profile.getMachineSetting('machine_name') == '':
            log.debug('Machine name not found')
            return 

        # self.mainWindow.OnDropFiles(self.loadFiles)
        # TODO: load files on drop

        # app_version = version.getVersion(False)
        # if profile.getPreference('last_run_version') != app_version:
        #     profile.putPreference('last_run_version', app_version)
        #     newVersionDialog.newVersionDialog().Show()

        # setFullScreenCapable(self.mainWindow)
