# -*- coding: utf-8 -*-

from PySide import QtCore, QtGui

from mainwindow_ui import Ui_MainWindow
from omni3dapp.util import profile
from omni3dapp.gui.util.gcode_text_styling import GCodeSyntaxHighlighter
from omni3dapp.gui import sceneview
from omni3dapp.logger import log


class MainWindow(QtGui.QMainWindow):

    NORMAL_MODE_ONLY_ITEMS = [
            'Open_Profile',
            'Save_Profile',
            'Load_Profile_from_GCode',
            'Reset_Profile_to_default',
            'Open_expert_settings',
            ]

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.set_up_fields()
        self.setup_scene()
        self.connect_actions()

        # self.timer = QtCore.QTimer(self)
        # self.timer.timeout.connect(self.onTimer)
        # self.timer.start(1000)

        self.lastTriedClipboard = profile.getProfileString()

        self.update_slice_mode()
        self.scene.setFocus()

    def setup_scene(self):
        self.scene = sceneview.SceneView(self)
        # sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.ui.right_widget.sizePolicy().hasHeightForWidth())
        # self.scene.setSizePolicy(sizePolicy)
        # self.scene.setObjectName("scene")
        # self.ui.horizontalLayout_3.removeWidget(self.ui.right_widget)
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
                elem.setToolTip(val.getTooltip())
            except Exception, e:
                log.debug('Could not set value to field {0}: {1}'.format(key, e))

    def connect_actions(self):
        self.ui.actionSwitch_to_quickprint.triggered.connect(self.on_simple_switch)
        self.ui.actionSwitch_to_expert_mode.triggered.connect(self.on_normal_switch)

        # Simple panel actions
        self.ui.high_quality.toggled.connect(self.scene.sceneUpdated)
        self.ui.normal_quality.toggled.connect(self.scene.sceneUpdated)
        self.ui.fast_low_quality.toggled.connect(self.scene.sceneUpdated)
        self.ui.pla.toggled.connect(self.scene.sceneUpdated)
        self.ui.abs.toggled.connect(self.scene.sceneUpdated)
        self.ui.simple_filament_diameter.textChanged.connect(
                self.scene.sceneUpdated)
        self.ui.print_support_structure.stateChanged.connect(
                self.scene.sceneUpdated)

        # Normal panel actions
        self.connect_actions_normal_mode()

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
        super(normalSettingsPanel, self).updateProfileToControls()

        # TODO - loading files to start_end_gcode panel:
        # if self.alterationPanel is not None:
        #     self.alterationPanel.updateProfileToControls()

        # TODO - loading plugins:
        # self.pluginPanel.updateProfileToControls()

    def update_profile_to_controls_all(self):
        self.scene.updateProfileToControls()
        self.update_profile_to_controls_normal_panel()

    def on_setting_change(self, *args, **kwargs):
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

    def add_to_model_mru(self, filename):
        action_file = QtGui.QAction(self)
        # action_file.setText(QtGui.QApplication.translate("MainWindow", filename, None, QtGui.QApplication.UnicodeUTF8))
        action_file.setText(filename)
        self.ui.menuRecent_Model_Files.addAction(action_file)
        # TODO: connect action


class NormalModeValidator(QtGui.QValidator):
    def validate(self):
        # must be implemented by every subclass. It returns Invalid,
        # Intermediate or Acceptable depending on whether its argument
        # is valid (for the subclass's definition of valid).
        super(NormalModeValidator, self).validate()

    def fixup(self):
        #  provided for validators that can repair some user errors
        super(NormalModeValidator, self).fixup()
