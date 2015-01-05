# -*- coding: utf-8 -*-

import os
import sys
import esky
import platform
import shutil
import glob
from urllib2 import URLError

from PySide import QtCore, QtGui, QtDeclarative, QtOpenGL

from mainwindow import MainWindow

# from omni3dapp.gui.sceneview import SceneView
from omni3dapp.gui.graphicsscene import SceneView
# from omni3dapp.gui.samplegl import OpenGLScene
from omni3dapp.logger import log
from omni3dapp.util import profile


YES_BTN = QtGui.QMessageBox.Yes
NO_BTN = QtGui.QMessageBox.No

UPDATES_URL = "http://localhost:8080/"


class OmniApp(object):

    def __init__(self, files):
        app = QtGui.QApplication(sys.argv)

        self.main_window = None
        self.splash = None
        self.load_files = files

        # QtDeclarative.qmlRegisterType(SampleGLView, 'Sample', 1, 0,
        #         'SampleGLView')

        if sys.platform.startswith('darwin'):
            # Do not show a splashscreen on OSX, as by Apple guidelines
            self.after_splash()
        else:
            self.set_splash_screen()
            self.splash.show()
            app.processEvents()
            self.after_splash()
        # self.main_window = QtDeclarative.QDeclarativeView()
        # engine = self.main_window.engine()
        # engine.quit.connect(app.quit)
        # self.main_window.setSource(QtCore.QUrl(self.find_data_file("qml/main.qml")))
        gl_format = QtOpenGL.QGLFormat()
        gl_format.setSampleBuffers(True)
        gl_widget = QtOpenGL.QGLWidget(gl_format)

        self.main_window = MainWindow()
        self.main_window.setViewport(gl_widget)
        self.main_window.setViewportUpdateMode(QtGui.QGraphicsView.FullViewportUpdate)

        self.scene = SceneView(self.main_window)

        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Base, QtCore.Qt.transparent)

        self.qmlview = QtDeclarative.QDeclarativeView()
        self.qmlview.rootContext().setContextProperty("mainwindow", self)
        self.qmlview.rootContext().setContextProperty(
            "graphicsscene", self.scene)
        self.qmlview.setSource(QtCore.QUrl(self.main_window.find_data_file("qml/main.qml")))

        self.qmlview.setPalette(palette)

        # self.setCentralWidget(self.qmlview)
        # self.scene.setCentralWidget(self.qmlview)

        self.scene.addWidget(self.qmlview)
        self.qmlview.move(QtCore.QPoint(0,0))
        self.qmlview.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.main_window.setScene(self.scene)

        self.main_window.resize(1024, 768)

        self.splash.finish(self.main_window)
        self.main_window.show()

        if profile.getPreference('check_for_updates') == 'True' and \
                hasattr(sys, 'frozen'):
            try:
                self.check_for_updates()
            except Exception as e:
                log.error("Something went wrong while fetching updates: {0}".format(e))

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
                    executable = pathjoin(appdir, nm, sys.executable.split("\\")[-1])
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
