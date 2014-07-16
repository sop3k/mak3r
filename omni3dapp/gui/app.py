# -*- coding: utf-8 -*-

import sys
from PySide import QtGui

from mainwindow import Ui_MainWindow
from omniapp.logger import log


class MainWindow(QtGui.QMainWindow):
  def __init__(self, parent=None):
    super(MainWindow, self).__init__(parent)
    self.ui =  Ui_MainWindow()
    self.ui.setupUi(self)


class OmniApp(object):

    def load_previous_preferences(self):
        otherCuraInstalls = profile.getAlternativeBasePaths()
        otherCuraInstalls.sort()
        if len(otherCuraInstalls) > 0:
            profile.loadPreferences(os.path.join(otherCuraInstalls[-1], 'preferences.ini'))
            profile.loadProfile(os.path.join(otherCuraInstalls[-1], 'current_profile.ini'))

    def run_config_wizard(self):
        if platform.system() == "Windows":
            exampleFile = os.path.normpath(os.path.join(resources.resourceBasePath, 'example', 'UltimakerRobot_support.stl'))
        else:
            #Check if we need to copy our examples
            exampleFile = os.path.expanduser('~/CuraExamples/UltimakerRobot_support.stl')
            if not os.path.isfile(exampleFile):
                try:
                    os.makedirs(os.path.dirname(exampleFile))
                except Exception, e:
                    log.error(e)
                for filename in glob.glob(os.path.normpath(os.path.join(resources.resourceBasePath, 'example', '*.*'))):
                    shutil.copy(filename, os.path.join(os.path.dirname(exampleFile), os.path.basename(filename)))
        self.loadFiles = [exampleFile]
        #if self.splash is not None:
        #    self.splash.Show(False)
        #configWizard.configWizard()

    def check_for_updates(self, new_version):
        if newVersion is not None:
            #if self.splash is not None:
            #    self.splash.Show(False)
            #if wx.MessageBox(_("A new version of Cura is available, would you like to download?"), _("New version available"), wx.YES_NO | wx.ICON_INFORMATION) == wx.YES:
            #    webbrowser.open(new_version)
            #    return True

    def after_splash_callback(self):
        from util import resources, profile, version
        resources.setupLocalization(profile.getPreference('language'))

        #If we do not have preferences yet, try to load it from a previous Cura install
        if profile.getMachineSetting('machine_type') == 'unknown':
            try:
                self.load_previous_preferences()
            except Exception, e:
                import traceback
                print traceback.print_exc()
                log.error(e)

        #If we haven't run it before, run the configuration wizard.
        #if profile.getMachineSetting('machine_type') == 'unknown':
        #    self.run_config_wizard()    

        #if profile.getPreference('check_for_updates') == 'True':
        #    res = self.check_for_updates(version.checkForNewerVersion())
        #    if res:
        #        return

        if profile.getMachineSetting('machine_name') == '':
            log.debug('Machine name not found')
            return

        #self.mainWindow = mainWindow.mainWindow()
        #if self.splash is not None:
        #    self.splash.Show(False)
        #self.SetTopWindow(self.mainWindow)
        #self.mainWindow.Show()
        #self.mainWindow.OnDropFiles(self.loadFiles)
        main_window = MainWindow()
        main_window.show()
        sys.exit(app.exec_())
        # TODO: load files on drop

        #app_version = version.getVersion(False)
        #if profile.getPreference('last_run_version') != app_version:
        #    profile.putPreference('last_run_version', app_version)
        #    newVersionDialog.newVersionDialog().Show()

        #setFullScreenCapable(self.mainWindow)

        #if sys.platform.startswith('darwin'):
        #    wx.CallAfter(self.StupidMacOSWorkaround)


    def start_app():
        app = QtGui.QApplication(sys.argv)
        # TODO: Show splashscreen as imports take time
        # Use this method as callback
        self.after_splash_callback()
