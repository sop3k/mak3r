# -*- coding: utf-8 -*-

import re
import os
import sys
import subprocess
import traceback

from PySide import QtCore, QtGui, QtDeclarative

from omni3dapp.util import profile
from omni3dapp.util.printing import host
from omni3dapp.gui.util.gcode_text_styling import GCodeSyntaxHighlighter
from omni3dapp.gui.graphicsscene import SceneView
from omni3dapp.logger import log


class MainWindow(QtGui.QGraphicsView):

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
    SETTING_CHANGE_WHITELIST = [
            'commandbox',
            'logbox',
            'port_type',
            'port_baud_rate',
            'qt_spinbox_lineedit',
            ]
    TEXT_SETTINGS = [
            'startgcode',
            'endgcode',
            'machine_name'
            ]

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.model_files_history = QtCore.QSettings(
                '/'.join([profile.getBasePath(), 'mru_filelist.ini']),
                QtCore.QSettings.IniFormat)
        self.model_files_history_actions = []

        # self.ui = Ui_MainWindow()
        # self.ui.setupUi(self)

        # Create a scene to present and modify 3d objects
        self.setup_qmlview()

        self.print_button = self.qmlobject.findChild(
            QtCore.QObject, "print_button")

        self.top_bar = self.qmlobject.findChild(
            QtCore.QObject, "bars")

        self.advanced_options = self.qmlobject.findChild(
            QtCore.QObject, "options_layer")

        self.setup_scene()

        # If we haven't run it before, run the configuration wizard.
        if not profile.getMachineSetting('machine_name'):
            self.runConfigWizard()

        # if profile.getMachineSetting('machine_name') == '':
        #     log.debug('Machine name not found')
        #     # Notify that we need to have at least one machine
        #     return

        self.setUpFields()

        # Class that enables connecting to printer
        self.pc = host.PrinterConnection(self)

        # self.connect_actions()
        # self.connect_buttons()

        # As a printer is not connected at the start of the app, set the gui
        # disconnected
        # self.enable_elements(False)

        # self.timer = QtCore.QTimer(self)
        # self.timer.timeout.connect(self.onTimer)
        # self.timer.start(1000)

        # self.lastTriedClipboard = profile.getProfileString()

        # self.update_slice_mode()

    def resizeEvent(self, event):
        scene = self.scene()
        if scene:
            new_rect = QtCore.QRect(QtCore.QPoint(0, 0), event.size())
            scene.setSceneRect(new_rect)

        self.qmlview.setGeometry(new_rect)

        super(MainWindow, self).resizeEvent(event)

    def find_data_file(self, filename):
        if hasattr(sys, 'frozen'):
            datadir = os.path.dirname(sys.executable)
        else:
            datadir = os.path.dirname(__file__)
        return os.path.join(datadir, filename)

    def setup_qmlview(self):
        self.qmlview = QtDeclarative.QDeclarativeView()
        self.qmlview.setSource(QtCore.QUrl(self.find_data_file("qml/main.qml")))
        self.qmlview.setMinimumWidth(1000)
        self.qmlview.setMinimumHeight(600)
        self.qmlview.setResizeMode(self.qmlview.SizeRootObjectToView)

        self.qmlobject = self.qmlview.rootObject()

    def setup_scene(self):
        self.sceneview = SceneView(self)

        self.qmlview.rootContext().setContextProperty(
            "graphicsscene", self.sceneview)
        self.qmlview.rootContext().setContextProperty(
            "mainwindow", self)

        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Base, QtCore.Qt.transparent)
        self.qmlview.setPalette(palette)

        self.sceneview.addWidget(self.qmlview)
        self.qmlview.move(QtCore.QPoint(0,0))
        self.qmlview.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.setScene(self.sceneview)

    def runConfigWizard(self):
        self.wizard = self.qmlobject.findChild(
            QtCore.QObject, "wizard")
        self.wizard.showLayer()

    def setUpFields(self):
        field_vals = {}
        for key, val in profile.settingsDictionary.iteritems():
            field_vals[key] = val.getValue()

        self.advanced_options.setFields(field_vals)

        # startgcode = self.advanced_options.findChild(
        #     QtCore.QObject, "startgcode")
        # GCodeSyntaxHighlighter(startgcode)

        # endgcode = self.advanced_options.findChild(
        #     QtCore.QObject, "endgcode")
        # GCodeSyntaxHighlighter(endgcode)

    @QtCore.Slot()
    def saveAdvancedOptions(self):
        self.sceneview.setInfoText(_("Saving options..."))

        field_vals = self.advanced_options.getFields()
        for key, val in field_vals.iteritems():
            if isinstance(val, bool):
                self.onBoolSettingChange(key, val)
            elif key in self.TEXT_SETTINGS:
                self.changeSetting(key, val)
            else:
                self.onFloatSettingChange(key, val)

    @QtCore.Slot()
    def saveMachineSettings(self):
        field_vals = self.wizard.getMachineSettings()

        for key, val in field_vals.iteritems():
            if not isinstance(val, bool) and key not in self.TEXT_SETTINGS:
                try:
                    val = float(val)
                except ValueError:
                    pass
            profile.putMachineSetting(key, val)

        self.sceneview.resetMachineSize()

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

            # Create history for commandbox
            self.ui.commandbox.history = [u""]
            self.ui.commandbox.histindex = 1

    # def connect_actions(self):
    #     self.ui.actionSwitch_to_quickprint.triggered.connect(self.on_simple_switch)
    #     self.ui.actionSwitch_to_expert_mode.triggered.connect(self.on_normal_switch)
    #     self.ui.actionLoad_model_file_tCTRL_L.triggered.connect(self.scene.showLoadModel)
    #     self.ui.actionSave_model.triggered.connect(self.scene.showSaveModel)
    #     self.ui.actionReload_platform.triggered.connect(self.scene.reloadScene)
    #     self.ui.actionClear_platform.triggered.connect(self.scene.onDeleteAll)
    #     self.ui.actionPrint.triggered.connect(self.scene.onPrintButton)
    #     self.ui.actionSave_GCode.triggered.connect(self.scene.showSaveGCode)

    #     self.ui.commandbox.returnPressed.connect(self.pc.sendline)
    #     self.ui.commandbox.installEventFilter(self)

    #     for elem in self.ui.moveAxesBox.findChildren(QtGui.QPushButton):
    #         if elem.objectName().startswith('move'):
    #             elem.clicked.connect(self.move_axis)
    #         else:
    #             elem.clicked.connect(self.home_pos)

    #     # Simple panel actions
    #     self.connect_actions_simple_mode()
    #     # Normal panel actions
    #     self.connect_actions_normal_mode()

    # def connect_actions_simple_mode(self):
    #     self.ui.high_quality.toggled.connect(self.scene.sceneUpdated)
    #     self.ui.normal_quality.toggled.connect(self.scene.sceneUpdated)
    #     self.ui.fast_low_quality.toggled.connect(self.scene.sceneUpdated)
    #     self.ui.pla.toggled.connect(self.scene.sceneUpdated)
    #     self.ui.abs.toggled.connect(self.scene.sceneUpdated)
    #     self.ui.simple_filament_diameter.textChanged.connect(
    #             self.scene.sceneUpdated)
    #     self.ui.print_support_structure.stateChanged.connect(
    #             self.scene.sceneUpdated)

    # def connect_actions_normal_mode(self):
    #     # For each element in self.normal or self.tabWidget
    #     for elem in self.ui.normal.findChildren(QtGui.QWidget):
    #         if elem.objectName() in self.SETTING_CHANGE_WHITELIST:
    #             continue
    #         if isinstance(elem, QtGui.QDoubleSpinBox):
    #             elem.valueChanged.connect(self.on_value_changed)
    #         elif isinstance(elem, QtGui.QCheckBox):
    #             elem.stateChanged.connect(self.on_state_changed)
    #         elif isinstance(elem, QtGui.QLineEdit):
    #             elem.textChanged.connect(self.on_text_changed)
    #         elif isinstance(elem, QtGui.QComboBox):
    #             elem.currentIndexChanged.connect(self.on_index_changed)

    # def connect_buttons(self):
    #     self.ui.connect_btn.clicked.connect(self.connect_printer)
    #     self.ui.port_btn.clicked.connect(self.pc.rescanports)
    #     self.ui.send_btn.clicked.connect(self.pc.sendline)
    #     self.ui.set_bedtemp_btn.clicked.connect(self.bedtemp)
    #     self.ui.set_printtemp_btn.clicked.connect(self.settemp)

    # def on_simple_switch(self, *args, **kwargs):
    #     profile.putPreference('startMode', 'Simple')
    #     self.update_slice_mode(is_simple=True)

    # def on_normal_switch(self, *args, **kwargs):
    #     profile.putPreference('startMode', 'Normal')
    #     self.update_slice_mode(is_simple=False)

    # def update_slice_mode(self, is_simple=None):
    #     if not is_simple:
    #         is_simple = profile.getPreference('startMode') == 'Simple'
    #     self.ui.slice_modes.setCurrentIndex(int(is_simple))

    #     for item in self.NORMAL_MODE_ONLY_ITEMS:
    #         action = self.findChild(QtGui.QAction, 'action{0}'.format(item))
    #         action.setEnabled(not is_simple)
    #     if is_simple:
    #         self.ui.actionSwitch_to_quickprint.setChecked(True)
    #         self.ui.actionSwitch_to_expert_mode.setChecked(False)
    #     else:
    #         self.ui.actionSwitch_to_expert_mode.setChecked(True)
    #         self.ui.actionSwitch_to_quickprint.setChecked(False)

    #     self.scene.updateProfileToControls()
    #     self.scene._scene.pushFree()

    # def setupSlice(self):
    #     put = profile.setTempOverride
    #     get = profile.getProfileSetting
    #     for setting in profile.settingsList:
    #         if not setting.isProfile():
    #             continue
    #         profile.setTempOverride(setting.getName(), setting.getDefault())

    #     if self.ui.print_support_structure.isChecked():
    #         put('support', _("Exterior Only"))

    #     nozzle_size = float(get('nozzle_size'))
    #     if self.ui.normal_quality.isChecked():
    #         put('layer_height', '0.2')
    #         put('wall_thickness', nozzle_size * 2.0)
    #         put('layer_height', '0.10')
    #         put('fill_density', '20')
    #     elif self.ui.fast_low_quality.isChecked():
    #         put('wall_thickness', nozzle_size * 2.5)
    #         put('layer_height', '0.20')
    #         put('fill_density', '10')
    #         put('print_speed', '60')
    #         put('cool_min_layer_time', '3')
    #         put('bottom_layer_speed', '30')
    #     elif self.ui.high_quality.isChecked():
    #         put('wall_thickness', nozzle_size * 2.0)
    #         put('layer_height', '0.06')
    #         put('fill_density', '20')
    #         put('bottom_layer_speed', '15')
    #     # elif self.printTypeJoris.GetValue():
    #     #     put('wall_thickness', nozzle_size * 1.5)

    #     put('filament_diameter', self.ui.filament_diameter.text())
    #     if self.ui.abs.isChecked():
    #         put('print_bed_temperature', '100')
    #         put('platform_adhesion', 'Brim')
    #         put('filament_flow', '107')
    #         put('print_temperature', '245')
    #     put('plugin_config', '')

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

    # def update_profile_to_controls_all(self):
    #     self.scene.updateProfileToControls()
    #     self.update_profile_to_controls_normal_panel()

    # def on_value_changed(self):
    #     elem = QtCore.QObject.sender(self)
    #     self.on_setting_change(elem.objectName(), elem.value())

    # def on_state_changed(self):
    #     elem = QtCore.QObject.sender(self)
    #     self.on_setting_change(elem.objectName(), elem.isChecked())

    # def on_text_changed(self):
    #     elem = QtCore.QObject.sender(self)
    #     self.on_setting_change(elem.objectName(), elem.text())

    # def on_index_changed(self):
    #     elem = QtCore.QObject.sender(self)
    #     self.on_setting_change(elem.objectName(),
    #             elem.itemText(elem.currentIndex()))

    # def on_setting_change(self, obj_name, value):
    #     try:
    #         profile.settingsDictionary[obj_name].setValue(value)
    #     except KeyError as e:
    #         log.error("Key not found in preferences: {0}".format(e))
    #     self.validate_normal_mode()

    @QtCore.Slot(str, str)
    def onFloatSettingChange(self, obj_name, value):
        try:
            value = float(value)
        except ValueError as e:
            log.error("Could not assign value {0} to setting {1}: {2}".format(
                value, obj_name, e))
            return
        self.changeSetting(obj_name, value)

    @QtCore.Slot(str, bool)
    def onBoolSettingChange(self, obj_name, value):
        try:
            value = bool(value)
        except ValueError as e:
            log.error("Could not assign value {0} to setting {1}: {2}".format(
                value, obj_name, e))
            return
        self.changeSetting(obj_name, value)

    @QtCore.Slot(str, str)
    def changeSetting(self, obj_name, value):
        try:
            profile.settingsDictionary[obj_name].setValue(value)
        except KeyError as e:
            log.error("Key not found in preferences: {0}".format(e))
        self.validateNormalMode()

    def validateNormalMode(self):
        # TODO: improve dictionary structure so that we can easily get normal
        # mode elements
        # for elem in normal_mode_elems:
        #     elem.validate()
        self.sceneview.sceneUpdated()

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
        self.sceneview.loadFiles([filename])

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

    def set_statusbar(self, msg):
        self.sceneview.setInfoText(msg)

    # def connect_printer(self):
    #     port_val = self.ui.port_type.itemText(self.ui.port_type.currentIndex())
    #     baud_val = 115200
    #     try:
    #         baud_val = int(self.ui.port_baud_rate.itemText(
    #             self.ui.port_baud_rate.currentIndex()))
    #     except (TypeError, ValueError), e:
    #         log.error(_("Could not parse baud rate: {0}".format(e)))
    #         traceback.print_exc(file = sys.stdout)
    #     return self.pc.connect(port_val, baud_val)

    @QtCore.Slot()
    def pausePrinting(self):
        self.pc.pause()

    @QtCore.Slot()
    def turnOffPrinter(self):
        ret = self.pc.off()
        self.sceneview.setProgressBar(0.0)
        self.set_statusbar(_("Printing cancelled"))
        return ret

    def settemp(self):
        temp = self.ui.print_temperature.text()
        self.pc.set_printtemp(temp)

    def bedtemp(self):
        temp = self.ui.print_bed_temperature.text()
        self.pc.set_bedtemp(temp)

    def is_online(self):
        return self.pc.p.online

    def terminate_thread(self, thread_name):
        try:
            thread = getattr(self.sceneview.engine, thread_name, None)
            if not thread:
                return None
            thread.terminate()
            del thread
        except Exception, e:
            log.debug("Error terminating thread: {0}".format(e))

    def terminate_threads(self):
        for thread_name in self.THREADS:
            self.terminate_thread(thread_name)

    def move_axis(self):
        elem = QtCore.QObject.sender(self)
        try:
            axis, direction, step = re.match('move_([xyz])_(down|up)(\d{1,2})',
                elem.objectName()).groups()
        except AttributeError, e:
            log.error("Clicked button does not have an expected name: \
                {0}".format(e))
            return
        func = getattr(self.pc, 'move_{0}'.format(axis), None)
        if not func:
            log.error("Did not find method move_{0} of the class {1}".format(axis,
                self.pc.__class__))
            return 
        multip = int(direction == 'up') or -1
        if step.startswith('0'):
            step = re.sub(r'(0*)(\d+)', r'\1.\2', step)
        step = float(step)
        if step == 0:
            return
        return func(step * multip)

    def home_pos(self):
        elem = QtCore.QObject.sender(self)
        try:
            axis = re.match('home_([xyz]+)', elem.objectName()).group(1)
        except AttributeError, e:
            log.error('Clicked button does not have an expected name: \
                {0}'.format(e))
            return
        return self.pc.home_position(axis)

    def enable_elements(self, enable=True):
        return
        # self.ui.commandbox.setEnabled(enable)
        # self.ui.send_btn.setEnabled(enable)
        # for elem in self.ui.moveAxesBox.findChildren(QtGui.QPushButton):
        #     elem.setEnabled(enable)

        # self.ui.set_bedtemp_btn.setEnabled(enable)
        # self.ui.set_printtemp_btn.setEnabled(enable)

    def set_connected(self):
        # self.enable_elements(True)

        # self.ui.connect_btn.setText(_("Disconnect"))
        # self.ui.connect_btn.setToolTip(_("Disconnect from the printer"))
        # self.ui.connect_btn.clicked.disconnect(self.connect_printer)
        # self.ui.connect_btn.clicked.connect(self.pc.disconnect)

        self.set_statusbar(_("Connected to printer."))

        if self.pc.fgcode:
            # self.sceneview.printButton.setDisabled(False)
            self.print_button.enable()

    def set_disconnected(self):
        # self.enable_elements(False)

        # self.ui.connect_btn.setText(_("Connect"))
        # self.ui.connect_btn.setToolTip(_("Connect with the printer"))
        # self.ui.connect_btn.clicked.disconnect(self.pc.disconnect)
        # self.ui.connect_btn.clicked.connect(self.connect_printer)

        self.set_statusbar(_("Disconnected."))

    def setPrintButton(self, time_info, params_info):
        self.print_button.setPrintTime(time_info)
        self.print_button.setPrintParams(params_info)

    def eventFilter(self, obj, evt):
        if obj == self.ui.commandbox:
            if evt.type() == QtCore.QEvent.KeyPress:
                code = evt.key()
                if code == QtCore.Qt.Key_Up:
                    self.pc.cbkey_action(-1)
                    return True
                elif code == QtCore.Qt.Key_Down:
                    self.pc.cbkey_action(1)
                    return True
            return False
        return super(MainWindow, self).eventFilter(obj, evt)

    def closeEvent(self, evt):
        # terminate all slicer-related threads
        # TODO: check if needed
        # self.terminate_threads()
        profile.saveProfile(allMachines=True)
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
