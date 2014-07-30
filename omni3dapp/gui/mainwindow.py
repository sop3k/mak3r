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

        self.setup_scene()
        self.set_up_fields()
        self.connect_actions()

    def setup_scene(self):
        self.scene = sceneview.SceneView(self)
        # sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        # sizePolicy.setHorizontalStretch(0)
        # sizePolicy.setVerticalStretch(0)
        # sizePolicy.setHeightForWidth(self.ui.right_widget.sizePolicy().hasHeightForWidth())
        # self.scene.setSizePolicy(sizePolicy)
        # self.scene.setObjectName("scene")
        self.ui.horizontalLayout_3.removeWidget(self.ui.right_widget)
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

    def on_simple_switch(self, *args, **kwargs):
        profile.putPreference('startMode', 'Simple')
        self.update_slice_mode(is_simple=True)

    def on_normal_switch(self, *args, **kwargs):
        profile.putPreference('startMode', 'Normal')
        self.update_slice_mode(is_simple=False)

    def update_slice_mode(self, is_simple):
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
        # self.scene.updateProfileToControls()
        # self.scene._scene.pushFree()

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
