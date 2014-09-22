# -*- coding: utf-8 -*-

import re
import subprocess
import traceback

from PySide import QtCore, QtGui

from mainwindow_ui import Ui_MainWindow
from omni3dapp.util import profile
from omni3dapp.util.printing import host
from omni3dapp.gui.util.gcode_text_styling import GCodeSyntaxHighlighter
from omni3dapp.gui import sceneview
from omni3dapp.logger import log


class MainWindow(QtGui.QMainWindow):

    MAX_MRU_FILES = 5
    NORMAL_MODE_ONLY_ITEMS = [
            'Open_Profile',
            'Save_Profile',
            'Load_Profile_from_GCode',
            'Reset_Profile_to_default',
            'Open_expert_settings',
            ]
    THREADS = [
            '_thread',
            'socket_listener_thread',
            'socket_connector_thread',
            'log_thread'
            ]

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.model_files_history = QtCore.QSettings(
                '/'.join([profile.getBasePath(), 'mru_filelist.ini']),
                QtCore.QSettings.IniFormat)
        self.model_files_history_actions = []

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.pc = host.PrinterConnection(self)

        self.set_up_fields()
        self.setup_scene()
        self.connect_actions()
        self.connect_buttons()

        # self.timer = QtCore.QTimer(self)
        # self.timer.timeout.connect(self.onTimer)
        # self.timer.start(1000)

        self.lastTriedClipboard = profile.getProfileString()

        self.update_slice_mode()
        self.scene.setFocus()

    def setup_scene(self):
        self.scene = sceneview.SceneView(self)
        self.ui.horizontalLayout_3.addWidget(self.scene)

    def set_up_fields(self):
        for key, val in profile.settingsDictionary.iteritems():
            elem = getattr(self.ui, key, None)
            if not elem:
                continue
            try:
                if isinstance(elem, (QtGui.QLineEdit, QtGui.QTextEdit)):
                    # Add syntax styling to gcode fields
                    if key.endswith('gcode'):
                        GCodeSyntaxHighlighter(elem)
                    elem.setText(val.getValue())
                    # if elem._validators:
                        # set validator    
                elif isinstance(elem, QtGui.QCheckBox):
                    elem.setChecked(val.getValue() == u'True')
                elif isinstance(elem, QtGui.QComboBox):
                    items = val.getType()
                    elem.addItems(items)
                    elem.setCurrentIndex(items.index(val.getValue()))
                elif isinstance(elem, QtGui.QDoubleSpinBox):
                    val_range = val.getRange()
                    if val_range:
                        if val_range[0] is not None:
                            elem.setMinimum(float(val_range[0]))
                        if val_range[1] is not None:
                            elem.setMaximum(float(val_range[1]))
                    elem.setValue(float(val.getValue()))
                elem.setToolTip(val.getTooltip())
            except Exception, e:
                log.debug('Could not set value to field {0}: {1}'.format(key, e))

            # Set recent MRU files list
            for elem in xrange(self.MAX_MRU_FILES):
                action = QtGui.QAction(self, visible=False,
                        triggered=self.open_model_file)
                action.setObjectName("recent_model_file_{0}".format(elem))
                self.model_files_history_actions.append(action)
                self.ui.menuRecent_Model_Files.addAction(action)
            self.update_mru_files_actions()

    def connect_actions(self):
        self.ui.actionSwitch_to_quickprint.triggered.connect(self.on_simple_switch)
        self.ui.actionSwitch_to_expert_mode.triggered.connect(self.on_normal_switch)
        self.ui.actionLoad_model_file_tCTRL_L.triggered.connect(self.scene.showLoadModel)
        self.ui.actionSave_model.triggered.connect(self.scene.showSaveModel)
        self.ui.actionReload_platform.triggered.connect(self.scene.reloadScene)
        self.ui.actionClear_platform.triggered.connect(self.scene.onDeleteAll)
        self.ui.actionPrint.triggered.connect(self.scene.onPrintButton)
        self.ui.actionSave_GCode.triggered.connect(self.scene.showSaveGCode)

        # Simple panel actions
        self.connect_actions_simple_mode()
        # Normal panel actions
        self.connect_actions_normal_mode()

    def connect_actions_simple_mode(self):
        self.ui.high_quality.toggled.connect(self.scene.sceneUpdated)
        self.ui.normal_quality.toggled.connect(self.scene.sceneUpdated)
        self.ui.fast_low_quality.toggled.connect(self.scene.sceneUpdated)
        self.ui.pla.toggled.connect(self.scene.sceneUpdated)
        self.ui.abs.toggled.connect(self.scene.sceneUpdated)
        self.ui.simple_filament_diameter.textChanged.connect(
                self.scene.sceneUpdated)
        self.ui.print_support_structure.stateChanged.connect(
                self.scene.sceneUpdated)

    def connect_actions_normal_mode(self):
        # For each element in self.normal or self.tabWidget
        for elem in self.ui.normal.findChildren(QtGui.QCheckBox):
            elem.stateChanged.connect(self.on_setting_change)
        for elem in self.ui.normal.findChildren(QtGui.QLineEdit):
            elem.textChanged.connect(self.on_setting_change)
        for elem in self.ui.normal.findChildren(QtGui.QComboBox):
            elem.currentIndexChanged.connect(self.on_setting_change)
        for elem in self.ui.normal.findChildren(QtGui.QListWidget):
            elem.currentItemChanged.connect(self.on_setting_change)

    def connect_buttons(self):
        self.ui.connect_button.clicked.connect(self.connect_printer)
        self.ui.port_btn.clicked.connect(self.pc.rescanports)

    def on_simple_switch(self, *args, **kwargs):
        profile.putPreference('startMode', 'Simple')
        self.update_slice_mode(is_simple=True)

    def on_normal_switch(self, *args, **kwargs):
        profile.putPreference('startMode', 'Normal')
        self.update_slice_mode(is_simple=False)

    def update_slice_mode(self, is_simple=None):
        if not is_simple:
            is_simple = profile.getPreference('startMode') == 'Simple'
        self.ui.slice_modes.setCurrentIndex(int(is_simple))

        for item in self.NORMAL_MODE_ONLY_ITEMS:
            action = self.findChild(QtGui.QAction, 'action{0}'.format(item))
            action.setEnabled(not is_simple)
        if is_simple:
            self.ui.actionSwitch_to_quickprint.setChecked(True)
            self.ui.actionSwitch_to_expert_mode.setChecked(False)
        else:
            self.ui.actionSwitch_to_expert_mode.setChecked(True)
            self.ui.actionSwitch_to_quickprint.setChecked(False)

        # Set splitter sash position & size
        # if isSimple:
        #     # Save normal mode sash
        #     self.normalSashPos = self.splitter.GetSashPosition()

        #     # Change location of sash to width of quick mode pane
        #     (width, height) = self.simpleSettingsPanel.GetSizer().GetSize()
        #     self.splitter.SetSashPosition(width, True)

        #     # Disable sash
        #     self.splitter.SetSashSize(0)
        # else:
        #     self.splitter.SetSashPosition(self.normalSashPos, True)
        #     # Enabled sash
        #     self.splitter.SetSashSize(4)

        # self.defaultFirmwareInstallMenuItem.Enable(firmwareInstall.getDefaultFirmware() is not None)
        # if profile.getMachineSetting('machine_type') == 'ultimaker2':
        #     self.bedLevelWizardMenuItem.Enable(False)
        #     self.headOffsetWizardMenuItem.Enable(False)
        # if int(profile.getMachineSetting('extruder_amount')) < 2:
        #     self.headOffsetWizardMenuItem.Enable(False)
        self.scene.updateProfileToControls()
        self.scene._scene.pushFree()

    def setupSlice(self):
        put = profile.setTempOverride
        get = profile.getProfileSetting
        for setting in profile.settingsList:
            if not setting.isProfile():
                continue
            profile.setTempOverride(setting.getName(), setting.getDefault())

        if self.ui.print_support_structure.isChecked():
            put('support', _("Exterior Only"))

        nozzle_size = float(get('nozzle_size'))
        if self.ui.normal_quality.isChecked():
            put('layer_height', '0.2')
            put('wall_thickness', nozzle_size * 2.0)
            put('layer_height', '0.10')
            put('fill_density', '20')
        elif self.ui.fast_low_quality.isChecked():
            put('wall_thickness', nozzle_size * 2.5)
            put('layer_height', '0.20')
            put('fill_density', '10')
            put('print_speed', '60')
            put('cool_min_layer_time', '3')
            put('bottom_layer_speed', '30')
        elif self.ui.high_quality.isChecked():
            put('wall_thickness', nozzle_size * 2.0)
            put('layer_height', '0.06')
            put('fill_density', '20')
            put('bottom_layer_speed', '15')
        # elif self.printTypeJoris.GetValue():
        #     put('wall_thickness', nozzle_size * 1.5)

        put('filament_diameter', self.ui.filament_diameter.text())
        if self.ui.abs.isChecked():
            put('print_bed_temperature', '100')
            put('platform_adhesion', 'Brim')
            put('filament_flow', '107')
            put('print_temperature', '245')
        put('plugin_config', '')

    # def onTimer(self, e):
    #     # Check if there is something in the clipboard
    #     profileString = ""
    #     try:
    #         if not wx.TheClipboard.IsOpened():
    #             if not wx.TheClipboard.Open():
    #                 return
    #             do = wx.TextDataObject()
    #             if wx.TheClipboard.GetData(do):
    #                 profileString = do.GetText()
    #             wx.TheClipboard.Close()

    #             startTag = "CURA_PROFILE_STRING:"
    #             if startTag in profileString:
    #                 #print "Found correct syntax on clipboard"
    #                 profileString = profileString.replace("\n","").strip()
    #                 profileString = profileString[profileString.find(startTag)+len(startTag):]
    #                 if profileString != self.lastTriedClipboard:
    #                     print profileString
    #                     self.lastTriedClipboard = profileString
    #                     profile.setProfileFromString(profileString)
    #                     self.scene.notification.message("Loaded new profile from clipboard.")
    #                     self.updateProfileToAllControls()
    #     except:
    #         print "Unable to read from clipboard"

    def update_profile_to_controls_normal_panel(self):
        pass
        # super(normalSettingsPanel, self).updateProfileToControls()

        # TODO - loading files to start_end_gcode panel:
        # if self.alterationPanel is not None:
        #     self.alterationPanel.updateProfileToControls()

        # TODO - loading plugins:
        # self.pluginPanel.updateProfileToControls()

    def update_profile_to_controls_all(self):
        self.scene.updateProfileToControls()
        self.update_profile_to_controls_normal_panel()

    def on_setting_change(self):
        # profile.settingsDictionary
        elem = QtCore.QObject.sender(self)
        if isinstance(elem, (QtGui.QLineEdit, QtGui.QTextEdit)):
            profile.settingsDictionary[elem.objectName()].setValue(elem.text())
        elif isinstance(elem, QtGui.QCheckBox):
            profile.settingsDictionary[elem.objectName()].setValue(elem.isChecked())
        elif isinstance(elem, QtGui.QComboBox):
            profile.settingsDictionary[elem.objectName()].setValue(
                    elem.itemText(elem.currentIndex()))
        self.validate_normal_mode()

    def validate_normal_mode(self):
        # TODO: improve dictionary structure so that we can easily get normal
        # mode elements
        # for elem in normal_mode_elems:
        #     elem.validate()
        self.scene.sceneUpdated()

    # def _validate(self):
    #     for setting in self.settingControlList:
    #         setting._validate()
    #     if self._callback is not None:
    #         self._callback()

    def get_model_files_history(self):
        files = self.model_files_history.value('modelFilesHistory') or []
        if not isinstance(files, list):
            files = [files]
        return files

    def open_model_file(self):
        sender = QtCore.QObject.sender(self)
        try:
            file_ix = re.match('recent_model_file_(\d)',
                    sender.objectName()).group(1)
        except AttributeError, e:
            log.error('Failed to open model file: {0}'.format(e))
            return

        files = self.get_model_files_history()
        try:
            filename = files[int(file_ix)]
        except (IndexError, ValueError), e:
            log.error("Failed to open model file: {0}".format(e))
            return
        self.add_to_model_mru(filename)

        # load model
        profile.putPreference('lastFile', filename)
        self.scene.loadFiles([filename])

    def add_to_model_mru(self, filename):
        files = self.get_model_files_history()
        try:
            files.remove(filename)
        except ValueError:
            pass
        files.insert(0, filename)
        del files[MainWindow.MAX_MRU_FILES:]
        self.model_files_history.setValue('modelFilesHistory', files)
        self.update_mru_files_actions()

    def update_mru_files_actions(self):
        files = self.get_model_files_history()
        files_no = len(files) or 0
        recent_files_no = min(files_no, MainWindow.MAX_MRU_FILES)
        if recent_files_no < 1:
            return

        for i in xrange(recent_files_no):
            filename = files[i]
            action = self.model_files_history_actions[i]
            text = "{0} {1}".format(i + 1, self.stripped_name(filename))
            action.setText(text)
            action.setData(filename)
            action.setVisible(True)

        for j in range(recent_files_no, MainWindow.MAX_MRU_FILES):
            self.model_files_history_actions[j].setVisible(False)

    def stripped_name(self, full_filename):
        return QtCore.QFileInfo(full_filename).fileName()

    def connect_printer(self):
        log.debug(_("Connecting..."))
        port_val = self.ui.port_type.itemText(self.ui.port_type.currentIndex())
        baud_val = 115200
        try:
            baud_val = int(self.ui.port_baud_rate.itemText(
                self.ui.port_baud_rate.currentIndex()))
        except (TypeError, ValueError), e:
            log.error(_("Could not parse baud rate: {0}".format(e)))
            traceback.print_exc(file = sys.stdout)
        return self.pc.connect(port_val, baud_val)

    def terminate_thread(self, thread_name):
        try:
            thread = getattr(self.scene._engine, thread_name, None)
            if not thread:
                return None
            thread.terminate()
            del thread
        except Exception, e:
            log.debug("Error terminating thread: {0}".format(e))

    def terminate_threads(self):
        for thread_name in self.THREADS:
            self.terminate_thread(thread_name)

    def closeEvent(self, evt):
        # terminate all slicer-related threads
        self.terminate_threads()
        super(MainWindow, self).closeEvent(evt)


class NormalModeValidator(QtGui.QValidator):
    def validate(self):
        # must be implemented by every subclass. It returns Invalid,
        # Intermediate or Acceptable depending on whether its argument
        # is valid (for the subclass's definition of valid).
        super(NormalModeValidator, self).validate()

    def fixup(self):
        #  provided for validators that can repair some user errors
        super(NormalModeValidator, self).fixup()
