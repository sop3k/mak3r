# -*- coding: utf-8 -*-

import re
import os
import sys

from PySide import QtCore, QtGui, QtDeclarative

from omniapp import BASE_DIR
from omni3dapp.util import profile
from omni3dapp.util.printing import host
from omni3dapp.gui.util.gcode_text_styling import GCodeSyntaxHighlighter
from omni3dapp.gui.graphicsscene import SceneView
from omni3dapp.logger import log


class MainWindow(QtGui.QGraphicsView):

    MAX_MRU_FILES = 5
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

        # Create a scene to present and modify 3d objects
        self.setupQmlView()

        self.print_button = self.findQmlObject("print_button")
        self.connect_button = self.findQmlObject("connect_button")
        self.top_bar = self.findQmlObject("bars")
        self.advanced_options = self.findQmlObject("options_layer")
        self.temp_gauges = self.findQmlObject("tempgauges")

        self.setupScene()

        # If we haven't run it before, run the configuration wizard.
        if not profile.getMachineSetting('machine_name'):
            self.runConfigWizard()

        self.setUpFields()

        # Class that enables connecting to printer
        self.pc = host.PrinterConnection(self)

    def findQmlObject(self, objectname):
        return self.qmlobject.findChild(QtCore.QObject, objectname)

    @property
    def gconsole(self):
        if not hasattr(self, '_gconsole'):
            self._gconsole = self.findQmlObject("gconsole")
        return self._gconsole

    @property
    def machineWidth(self):
        if not hasattr(self, '_machineWidth'):
            self._machineWidth = profile.getMachineSettingFloat(
                'machine_width')
        return self._machineWidth

    @property
    def machineHeight(self):
        if not hasattr(self, '_machineHeight'):
            self._machineHeight = profile.getMachineSettingFloat(
                'machine_height')
        return self._machineHeight

    @property
    def machineDepth(self):
        if not hasattr(self, '_machineDepth'):
            self._machineDepth = profile.getMachineSettingFloat(
                'machine_depth')
        return self._machineDepth

    def resizeEvent(self, event):
        scene = self.scene()
        if scene:
            new_rect = QtCore.QRect(QtCore.QPoint(0, 0), event.size())
            scene.setSceneRect(new_rect)

        self.qmlview.setGeometry(new_rect)

        super(MainWindow, self).resizeEvent(event)

    def setupQmlView(self):
        self.qmlview = QtDeclarative.QDeclarativeView()

        MAINQML_PATH = "omni3dapp/gui/qml/main.qml"
        qmlpath = getattr(sys, 'frozen', False) and \
            os.path.abspath(os.path.join(BASE_DIR, MAINQML_PATH)) or MAINQML_PATH

        url = QtCore.QUrl()
        url.setScheme("file")
        url.setEncodedPath(qmlpath)
        self.qmlview.setSource(url)
        self.qmlview.setMinimumWidth(1000)
        self.qmlview.setMinimumHeight(600)
        self.qmlview.setResizeMode(self.qmlview.SizeRootObjectToView)

        self.qmlobject = self.qmlview.rootObject()

    def setupScene(self):
        self.sceneview = SceneView(self)

        self.qmlview.rootContext().setContextProperty(
            "graphicsscene", self.sceneview)
        self.qmlview.rootContext().setContextProperty(
            "mainwindow", self)

        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Base, QtCore.Qt.transparent)
        self.qmlview.setPalette(palette)

        self.sceneview.addWidget(self.qmlview)
        self.qmlview.move(QtCore.QPoint(0, 0))
        self.qmlview.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        self.setScene(self.sceneview)

    def runConfigWizard(self):
        self.wizard = self.findQmlObject("wizard")
        self.wizard.showLayer()

    def setUpFields(self):
        field_vals = {}
        for key, val in profile.settingsDictionary.iteritems():
            field_vals[key] = val.getValue()

        self.advanced_options.setFields(field_vals)
        self.temp_gauges.setTemperatures(
            field_vals.get("print_temperature") or "",
            field_vals.get("print_bed_temperature" or ""))

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

    def validateMachineSettings(self, field_vals):
        empty = [key for key, val in field_vals.items() if
                 not isinstance(val, bool) and not val]
        if empty:
            self.wizard.validationError(
                _("Value of field {} cannot be empty".format(empty[0])))
            return False

        for key in ['machine_width', 'machine_height', 'machine_depth',
                    'nozzle_size']:
            try:
                float(field_vals[key])
            except ValueError:
                msg = _("Incorrect value for field {}.\n"
                        "It needs to be a correct number".format(key))
                self.wizard.validationError(msg)
                return False
        return True

    @QtCore.Slot()
    def saveMachineSettings(self):
        field_vals = self.wizard.getMachineSettings()
        valid = self.validateMachineSettings(field_vals)
        if not valid:
            return

        for key, val in field_vals.iteritems():
            if not isinstance(val, bool) and key not in self.TEXT_SETTINGS:
                val = float(val)
            profile.putMachineSetting(key, val)

        self.sceneview.resetMachineSize()
        self.wizard.configFinished()

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

    def getModelFilesHistory(self):
        files = self.model_files_history.value('modelFilesHistory') or []
        if not isinstance(files, list):
            files = [files]
        return files

    def addToModelMRU(self, filename):
        files = self.getModelFilesHistory()
        try:
            files.remove(filename)
        except ValueError:
            pass
        files.insert(0, filename)
        del files[MainWindow.MAX_MRU_FILES:]
        self.model_files_history.setValue('modelFilesHistory', files)
        self.updateMRUFilesActions()

    def updateMRUFilesActions(self):
        files = self.getModelFilesHistory()
        files_no = len(files) or 0
        recent_files_no = min(files_no, MainWindow.MAX_MRU_FILES)
        if recent_files_no < 1:
            return

        for i in xrange(recent_files_no):
            filename = files[i]
            action = self.model_files_history_actions[i]
            text = "{0} {1}".format(i + 1, self.strippedName(filename))
            action.setText(text)
            action.setData(filename)
            action.setVisible(True)

        for j in range(recent_files_no, MainWindow.MAX_MRU_FILES):
            self.model_files_history_actions[j].setVisible(False)

    def strippedName(self, full_filename):
        return QtCore.QFileInfo(full_filename).fileName()

    @QtCore.Slot(str)
    def setStatusbar(self, msg):
        log.debug(msg)
        self.sceneview.setInfoText(msg)

    @QtCore.Slot(float)
    def setProgress(self, value):
        if not hasattr(self, 'sceneview'):
            return
        self.sceneview.setProgressBar(value)

    def setHeatingFinished(self):
        if not hasattr(self, 'pc'):
            log.debug("Can't set heating finished - don't have pc object")
            return
        self.pc.heating_finished()

    @QtCore.Slot()
    def connectPrinter(self):
        self.setStatusbar(_("Connecting..."))
        if not self.isOnline():
            self.pc.start_connect_thread()
        else:
            self.setConnected()

    @QtCore.Slot()
    def disconnectPrinter(self):
        self.setStatusbar(_("Disconnecting..."))
        if not self.isOnline():
            self.setDisconnected()
        else:
            self.pc.disconnect()

    @QtCore.Slot()
    def pausePrinting(self):
        self.pc.pause()

    @QtCore.Slot()
    def resumePrinting(self):
        self.pc.resume()

    @QtCore.Slot()
    def turnOffPrinter(self):
        ret = self.pc.off()
        self.sceneview.setProgressBar(0.0)
        self.setStatusbar(_("Printing cancelled"))
        return ret

    def isOnline(self):
        if hasattr(self, 'pc'):
            return self.pc.p.online
        return False

    @QtCore.Slot(str)
    def setConnected(self, msg=None):
        msg = msg or _("Connected to printer")
        self.setStatusbar(msg)
        self.enablePrintButton(True)
        self.connect_button.setState("ONLINE")

    @QtCore.Slot(str)
    def setDisconnected(self, msg=None):
        self.connect_button.setState("OFFLINE")
        self.enablePrintButton(False)
        msg = msg or _("Printer disconnected")
        self.setStatusbar(msg)

    def setPrintButton(self, time_info, params_info):
        self.print_button.setPrintTime(time_info)
        self.print_button.setPrintParams(params_info)

    def enablePrintButton(self, enable):
        state = self.print_button.getState()
        if state == "IDLE" and self.isSlicingEnabled() or state == "SLICING":
            return self.print_button.enable()

        if enable and self.isPrintingEnabled():
            return self.print_button.enable()

        self.print_button.disable()

    def setPrintState(self, state):
        self.print_button.setState(state)

    def setPrintingGcode(self, gcode):
        self.pc.fgcode = gcode

    def isSlicingEnabled(self):
        if not hasattr(self, 'sceneview'):
            return False
        return self.sceneview.isSlicingEnabled()

    def isPrintingEnabled(self):
        if not hasattr(self, 'sceneview'):
            return False
        return self.sceneview.isPrintingEnabled()

    def validatedTemp(self, val):
        try:
            val = float(val)
        except ValueError as e:
            log.error("{0} is invalid temperature value: {1}".format(val, e))
            # TODO: Notify user to enter a valid value
            return None
        return val

    @QtCore.Slot(str)
    def setPrintTemp(self, val):
        temp = self.validatedTemp(val)
        if not temp:
            return
        self.changeSetting("print_temperature", temp)
        self.sceneview.setPrinttempTarget(temp)
        self.pc.set_printtemp(temp)
        self.pc.update_tempdisplay()

    @QtCore.Slot(str)
    def setBedTemp(self, val):
        temp = self.validatedTemp(val)
        if not temp:
            return
        self.changeSetting("print_bed_temperature", temp)
        self.sceneview.setBedtempTarget(temp)
        self.pc.set_bedtemp(temp)
        self.pc.update_tempdisplay()

    @QtCore.Slot(str)
    def sendCommand(self, command):
        self.pc.sendline(command)

    @QtCore.Slot(str)
    def homeAxis(self, axis):
        self.pc.home_position(axis)

    @QtCore.Slot(float)
    def moveX(self, step):
        self.pc.move_x(step, self.machineWidth)

    @QtCore.Slot(float)
    def moveY(self, step):
        self.pc.move_y(step, self.machineDepth)

    @QtCore.Slot(float)
    def moveZ(self, step):
        self.pc.move_z(step, self.machineHeight)

    def addToLogbox(self, text):
        self.gconsole.appendToLogbox(text)

    def closeEvent(self, evt):
        # terminate all slicer-related threads
        # TODO: check if needed
        profile.saveProfile(allMachines=True)
        self.sceneview.clear()
        evt.accept()


class NormalModeValidator(QtGui.QValidator):
    def validate(self):
        # must be implemented by every subclass. It returns Invalid,
        # Intermediate or Acceptable depending on whether its argument
        # is valid (for the subclass's definition of valid).
        super(NormalModeValidator, self).validate()

    def fixup(self):
        #  provided for validators that can repair some user errors
        super(NormalModeValidator, self).fixup()
