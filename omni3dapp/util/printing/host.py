import os
import Queue
import re
import sys
import time
import string
import traceback
import cStringIO as StringIO
import subprocess
import glob
import logging
try: import simplejson as json
except ImportError: import json

if os.name == "nt":
    try:
        import _winreg
    except:
        pass

from PySide import QtCore, QtGui

from serial import SerialException
from .utils import setup_logging, dosify, \
    iconfile, configfile, format_time, format_duration, \
    hexcolor_to_float, parse_temperature_report, \
    prepare_command, check_rgb_color, check_rgba_color

from omni3dapp.util import profile
from omni3dapp.util.printing.pronsole import Pronsole
from omni3dapp.util.printing import gcoder
from .pronsole import REPORT_NONE, REPORT_POS, REPORT_TEMP
from omni3dapp.logger import log


class GuiSignals(QtCore.QObject):
    addtext = QtCore.Signal(str)
    setonline = QtCore.Signal()
    setoffline = QtCore.Signal()
    enable_printing = QtCore.Signal()
    set_printtemp_target = QtCore.Signal(float)
    set_bedtemp_target = QtCore.Signal(float)
    set_printtemp_value = QtCore.Signal(float)
    set_bedtemp_value = QtCore.Signal(float)


class PrinterConnection(Pronsole):
    """
    Handles connecting to printer and storing a state of printing
    """
    _fgcode = None

    def _get_fgcode(self):
        return self._fgcode

    def _set_fgcode(self, value):
        self._fgcode = value
        self.excluder = None
        self.excluder_e = None
        self.excluder_z_abs = None
        self.excluder_z_rel = None
    fgcode = property(_get_fgcode, _set_fgcode)

    # def _get_display_graph(self):
    #     return self.settings.tempgraph
    # display_graph = property(_get_display_graph)

    def _get_display_gauges(self):
        # return self.settings.tempgauges
        return True
    display_gauges = property(_get_display_gauges)

    def __init__(self, parent):
        Pronsole.__init__(self, parent)
        self.parent = parent
        self.ui = parent.ui
        self.paused = False
        self.sdprinting = False
        self.pauseScript = "pause.gcode"
        self.endScript = "end.gcode"

        self.capture_skip = {}
        self.capture_skip_newline = False
        self.fgcode = None
        self.excluder = None
        self.slicep = None
        self.current_pos = [0, 0, 0]
        self.uploading = False
        self.sentlines = Queue.Queue(0)
        # self.cpbuttons = {
        #     "motorsoff": SpecialButton(_("Motors off"), ("M84"), (250, 250, 250), _("Switch all motors off")),
        #     "extrude": SpecialButton(_("Extrude"), ("pront_extrude"), (225, 200, 200), _("Advance extruder by set length")),
        #     "reverse": SpecialButton(_("Reverse"), ("pront_reverse"), (225, 200, 200), _("Reverse extruder by set length")),
        # }
        self.custombuttons = []
        self.btndict = {}
        self.filehistory = None
        self.autoconnect = False
        self.parse_cmdline(sys.argv[1:])
        # set feedrates in printcore for pause/resume
        try:
            self.p.xy_feedrate = profile.settingsDictionary.get('xy_feedrate').getValue()
        except AttributeError:
            self.p.xy_feedrate = ""
        try:
            self.p.z_feedrate = profile.settingsDictionary.get('z_feedrate').getValue()
        except AttributeError:
            self.p.z_feedrate = ""
        # TODO: adding custom buttons (?)
        # customdict = {}
        # try:
        #     execfile(configfile("custombtn.txt"), customdict)
        #     if len(customdict["btns"]):
        #         if not len(self.custombuttons):
        #             try:
        #                 self.custombuttons = customdict["btns"]
        #                 for n in xrange(len(self.custombuttons)):
        #                     self.cbutton_save(n, self.custombuttons[n])
        #                 os.rename("custombtn.txt", "custombtn.old")
        #                 rco = open("custombtn.txt", "w")
        #                 rco.write(_("# I moved all your custom buttons into .pronsolerc.\n# Please don't add them here any more.\n# Backup of your old buttons is in custombtn.old\n"))
        #                 rco.close()
        #             except IOError, x:
        #                 logging.error(str(x))
        #         else:
        #             logging.warning(_("Note!!! You have specified custom buttons in both custombtn.txt and .pronsolerc"))
        #             logging.warning(_("Ignoring custombtn.txt. Remove all current buttons to revert to custombtn.txt"))

        # except:
        #     pass
        # self.add_custom_buttons()

        # disable all printer controls until we connect to a printer
        # self.gui_set_disconnected()
        self.parent.set_statusbar(_("Not connected to printer."))
        self.stdout = sys.stdout
        self.slicing = False
        self.loading_gcode = False
        self.loading_gcode_message = ""
        self.mini = False
        self.p.sendcb = self.sentcb
        self.p.preprintsendcb = self.preprintsendcb
        self.p.printsendcb = self.printsentcb
        self.p.startcb = self.startcb
        self.p.endcb = self.endcb
        self.cur_button = None
        self.predisconnect_mainqueue = None
        self.predisconnect_queueindex = None
        self.predisconnect_layer = None
        self.hsetpoint = 0.0
        self.bsetpoint = 0.0
        if self.autoconnect:
            self.connect()

        printset = set(string.printable)
        self.is_printable = lambda text: set(text).issubset(printset)

        self.guisignals = GuiSignals()
        self.guisignals.addtext.connect(self.addtexttolog)
        self.guisignals.setonline.connect(self.online_gui) 
        self.guisignals.setoffline.connect(self.offline_gui) 
        self.guisignals.enable_printing.connect(
                self.parent.scene.enable_printing)
        self.guisignals.set_printtemp_target.connect(
                self.parent.scene.set_printtemp_target)
        self.guisignals.set_bedtemp_target.connect(
                self.parent.scene.set_bedtemp_target)
        self.guisignals.set_printtemp_value.connect(
                self.parent.scene.set_printtemp_value)
        self.guisignals.set_bedtemp_value.connect(
                self.parent.scene.set_bedtemp_value)

    def connect(self, port_val, baud_val):
        self.guisignals.addtext.emit(_('Connecting...'))
        if not port_val:
            port_val = self.rescanports()
            if not port_val:
                msg = _('Could not find active ports.')
                self.guisignals.addtext.emit(msg)
                return

        self.parent.set_statusbar(_("Connecting..."))

        if self.paused:
            self.p.paused = 0
            self.p.printing = 0
        #     wx.CallAfter(self.pausebtn.SetLabel, _("Pause"))
        #     wx.CallAfter(self.printbtn.SetLabel, _("Print"))
        #     wx.CallAfter(self.toolbarsizer.Layout)
            self.paused = 0
            if self.sdprinting:
                self.p.send_now("M26 S0")
        if not self.connect_to_printer(port_val, baud_val):
            return
        try:
            settings_port = profile.settingsDictionary.get('port_type').getValue()
        except AttributeError:
            settings_port = ""
        if port_val != settings_port:
            # profile.settingsDictionary['port_type'].setValue(port_val)
            profile.putMachineSetting('port_type', port_val)

        try:
            settings_baud = profile.settingsDictionary.get('port_baud_rate').getValue()
        except AttributeError:
            settings_baud = ""
        if baud_val != settings_baud:
            # profile.settingsDictionary['port_baud_rate'].setValue(baud_val)
            profile.putMachineSetting('port_baud_rate', baud_val)

        if self.predisconnect_mainqueue:
            # self.recoverbtn.Enable()
            pass

    def rescanports(self):
        scanned = self.scanserial()
        portslist = list(scanned)
        port = profile.settingsDictionary.get('port_type') or ""
        if port:
            port = port.getValue()
        if port != "" and port not in portslist:
            portslist.append(port)
        if portslist:    
            if not port:
                port = portslist[0]
            self.ui.port_type.clear()
            self.ui.port_type.addItems(portslist)
            self.parent.set_statusbar(_("Found active ports."))
        else:
            self.parent.set_statusbar(_("Did not find any connected ports."))
        if os.path.exists(port) or port in scanned:
            self.ui.port_type.setCurrentIndex(self.ui.port_type.findText(port))
        return port

    def store_predisconnect_state(self):
        self.predisconnect_mainqueue = self.p.mainqueue
        self.predisconnect_queueindex = self.p.queueindex
        self.predisconnect_layer = self.curlayer

    def logdisp(self, msg, error=False):
        if error:
            log.error(msg)
        else:
            log.debug(msg)
        self.guisignals.addtext.emit(msg)

    def disconnect(self):
        self.parent.set_statusbar(_("Disconnecting from printer..."))
        if self.p.printing or self.p.paused or self.paused:
            self.store_predisconnect_state()
        self.p.signals.disconnect_sig.emit()
        self.statuscheck = False
        if self.status_thread:
            self.status_thread.terminate()
            self.status_thread = None

        # wx.CallAfter(self.connectbtn.SetLabel, _("Connect"))
        # wx.CallAfter(self.connectbtn.SetToolTip, wx.ToolTip(_("Connect to the printer")))
        # wx.CallAfter(self.connectbtn.Bind, wx.EVT_BUTTON, self.connect)

        # wx.CallAfter(self.gui_set_disconnected)

        if self.paused:
            self.p.paused = 0
            self.p.printing = 0
            # wx.CallAfter(self.pausebtn.SetLabel, _("Pause"))
            # wx.CallAfter(self.printbtn.SetLabel, _("Print"))
            self.paused = 0
            if self.sdprinting:
                self.p.send_now("M26 S0")

        # Relayout the toolbar to handle new buttons size
        # wx.CallAfter(self.toolbarsizer.Layout)

    @QtCore.Slot(str)
    def addtexttolog(self, text):
        if self.is_printable(text):
            self.ui.logbox.appendPlainText(text)
            # max_length = 20000
            # current_length = self.logbox.GetLastPosition()
            # if current_length > max_length:
            #     self.logbox.Remove(0, current_length / 10)
        else:
            msg = _("Attempted to write invalid text to console, which could be due to an invalid baudrate")
            log.debug(msg)
            self.ui.logbox.appendPlainText(msg)

    def sentcb(self, line, gline):
        """Callback when a printer gcode has been sent"""
        if not gline:
            pass
        elif gline.command in ["M104", "M109"]:
            gline_s = gcoder.S(gline)
            if gline_s is not None:
                temp = gline_s
                #if self.display_gauges: wx.CallAfter(self.hottgauge.SetTarget, temp)
                if self.display_gauges:
                    # self.hottgauge.setTarget(temp)
                    self.guisignals.set_printtemp_target.emit(temp)
                # if self.display_graph: wx.CallAfter(self.graph.SetExtruder0TargetTemperature, temp)
                # if self.display_graph:
                #     self.graph.SetExtruder0TargetTemperature(temp)
        elif gline.command in ["M140", "M190"]:
            gline_s = gcoder.S(gline)
            if gline_s is not None:
                temp = gline_s
                if self.display_gauges:
                    # self.bedtgauge.SetTarget(temp)
                    self.guisignals.set_bedtemp_target.emit(temp)
                # if self.display_graph:
                #     self.graph.SetBedTargetTemperature(temp)
        elif gline.command.startswith("T"):
            tool = gline.command[1:]
            if hasattr(self, "extrudersel"):
                self.extrudersel.SetValue(tool)
        self.sentlines.put_nowait(line)

    def is_excluded_move(self, gline):
        """Check whether the given moves ends at a position specified as
        excluded in the part excluder"""
        if not gline.is_move or not self.excluder or not self.excluder.rectangles:
            return False
        for (x0, y0, x1, y1) in self.excluder.rectangles:
            if x0 <= gline.current_x <= x1 and y0 <= gline.current_y <= y1:
                return True
        return False

    def preprintsendcb(self, gline, next_gline):
        """Callback when a printer gcode is about to be sent. We use it to
        exclude moves defined by the part excluder tool"""
        if not self.is_excluded_move(gline):
            return gline
        else:
            if gline.z is not None:
                if gline.relative:
                    if self.excluder_z_abs is not None:
                        self.excluder_z_abs += gline.z
                    elif self.excluder_z_rel is not None:
                        self.excluder_z_rel += gline.z
                    else:
                        self.excluder_z_rel = gline.z
                else:
                    self.excluder_z_rel = None
                    self.excluder_z_abs = gline.z
            if gline.e is not None and not gline.relative_e:
                self.excluder_e = gline.e
            # If next move won't be excluded, push the changes we have to do
            if next_gline is not None and not self.is_excluded_move(next_gline):
                if self.excluder_e is not None:
                    self.p.send_now("G92 E%.5f" % self.excluder_e)
                    self.excluder_e = None
                if self.excluder_z_abs is not None:
                    if gline.relative:
                        self.p.send_now("G90")
                    self.p.send_now("G1 Z%.5f" % self.excluder_z_abs)
                    self.excluder_z_abs = None
                    if gline.relative:
                        self.p.send_now("G91")
                if self.excluder_z_rel is not None:
                    if not gline.relative:
                        self.p.send_now("G91")
                    self.p.send_now("G1 Z%.5f" % self.excluder_z_rel)
                    self.excluder_z_rel = None
                    if not gline.relative:
                        self.p.send_now("G90")
                return None

    def printsentcb(self, gline):
        """Callback when a print gcode has been sent"""
        if gline.is_move:
            if hasattr(self.gwindow, "set_current_gline"):
                wx.CallAfter(self.gwindow.set_current_gline, gline)
            if hasattr(self.gviz, "set_current_gline"):
                wx.CallAfter(self.gviz.set_current_gline, gline)

    def startcb(self, resuming=False):
        """Callback on print start"""
        Pronsole.startcb(self, resuming)
        # TODO: locking interface dependent on settings
        # if self.settings.lockbox and self.settings.lockonstart:
        #     wx.CallAfter(self.lock, force = True)

    def endcb(self):
        """Callback on print end/pause"""
        Pronsole.endcb(self)
        if self.p.queueindex == 0:
            self.p.runSmallScript(self.endScript)
            self.parent.scene.on_endprint()
            # wx.CallAfter(self.pausebtn.Disable)
            # wx.CallAfter(self.printbtn.SetLabel, _("Print"))
            # wx.CallAfter(self.toolbarsizer.Layout)

    def move_axis(self, axis, curr_pos, step, mach_size):
        print self.current_pos
        # self.zb.clearRepeat()
        if step == 0:
            return
        offset = profile.getMachineSettingFloat('machine_{0}_offset'.format(axis))
        # if self.settings.clamp_jogging:
        new_pos = curr_pos + step
        print new_pos
        # if new_x < x_offset or new_x > mach_width + x_offset:
        if new_pos > mach_size + offset or new_pos < 0:
            self.clamped_move_message()
            return
        self.onecmd('move {0} {1}'.format(axis.upper(), step))
        self.p.send_now('M114')

    def move_x(self, step):
        mach_width = profile.getMachineSettingFloat('machine_width') 
        self.move_axis('x', self.current_pos[0], step, mach_width)

    def move_y(self, step):
        mach_depth = profile.getMachineSettingFloat('machine_depth')
        self.move_axis('y', self.current_pos[1], step, mach_depth)

    def move_z(self, step):
        mach_height = profile.getMachineSettingFloat('machine_height')
        self.move_axis('z', self.current_pos[2], step, mach_height)
        # When user clicks on the Z control, the XY control no longer gets spacebar/repeat signals
        # self.xyb.clearRepeat()

    def home_position(self, axis):
        if axis == 'all':
            self.onecmd('home')
        self.onecmd('home {0}'.format(axis.upper()))
        self.p.send_now('M114')

    def statuschecker(self):
        Pronsole.statuschecker(self)
        self.parent.set_statusbar(_("Not connected to printer."))

    def pause(self, button):
        print "inside pause"
        if not self.paused:
            self.log(_("Print paused at: %s") % format_time(time.time()))
            if self.sdprinting:
                self.p.send_now("M25")
            else:
                if not self.p.printing:
                    return
                self.p.pause()
                self.p.runSmallScript(self.pauseScript)
            self.paused = True
            # self.p.runSmallScript(self.pauseScript)
            self.extra_print_time += int(time.time() - self.starttime)
            self.parent.scene.on_pauseprint()
            # wx.CallAfter(self.pausebtn.SetLabel, _("Resume"))
            # wx.CallAfter(self.toolbarsizer.Layout)
        else:
            self.log(_("Resuming."))
            self.paused = False
            if self.sdprinting:
                self.p.send_now("M24")
            else:
                self.p.resume()
            self.parent.scene.on_resumeprint()
            # wx.CallAfter(self.pausebtn.SetLabel, _("Pause"))
            # wx.CallAfter(self.toolbarsizer.Layout)

    def recover(self, event):
        self.extra_print_time = 0
        if not self.p.online:
            wx.CallAfter(self.statusbar.SetStatusText, _("Not connected to printer."))
            return
        # Reset Z
        self.p.send_now("G92 Z%f" % self.predisconnect_layer)
        # Home X and Y
        self.p.send_now("G28 X Y")
        self.on_startprint()
        self.p.startprint(self.predisconnect_mainqueue, self.p.queueindex)

    def reset(self, event):
        self.log(_("Reset."))
        dlg = wx.MessageDialog(self, _("Are you sure you want to reset the printer?"), _("Reset?"), wx.YES | wx.NO)
        if dlg.ShowModal() == wx.ID_YES:
            self.p.reset()
            self.sethotendgui(0)
            self.setbedgui(0)
            self.p.printing = 0
            wx.CallAfter(self.printbtn.SetLabel, _("Print"))
            if self.paused:
                self.p.paused = 0
                wx.CallAfter(self.pausebtn.SetLabel, _("Pause"))
                self.paused = 0
            wx.CallAfter(self.toolbarsizer.Layout)
        dlg.Destroy()

    def process_host_command(self, command):
        """Override host command handling"""
        command = command.lstrip()
        if command.startswith(";@pause"):
            self.pause(None)
        else:
            pronsole.pronsole.process_host_command(self, command)

    def online(self):
        """Callback when printer goes online"""
        msg = _("Printer is now online.")
        self.log(msg)
        self.guisignals.addtext.emit(msg)
        self.guisignals.setonline.emit()
        self.guisignals.enable_printing.emit()
        self.parent.scene.printtemp_gauge.setHidden(False)
        self.parent.scene.bedtemp_gauge.setHidden(False)

    @QtCore.Slot()
    def online_gui(self):
        """Callback when printer goes online (graphical bits)"""
        self.parent.set_connected()

        self.ui.connect_btn.setText(_("Disconnect"))
        self.ui.connect_btn.setToolTip(_("Disconnect from the printer"))
        self.ui.connect_btn.clicked.disconnect(self.parent.connect_printer)
        self.ui.connect_btn.clicked.connect(self.disconnect)

        self.parent.set_statusbar(_("Connected to printer."))

    #     if hasattr(self, "extrudersel"):
    #         self.do_tool(self.extrudersel.GetValue())

    #     self.gui_set_connected()

    #     if self.filename:
    #         self.printbtn.Enable()

    #     wx.CallAfter(self.toolbarsizer.Layout)

    @QtCore.Slot()
    def offline_gui(self):
        self.parent.set_connected(False)

        self.ui.connect_btn.setText(_("Connect"))
        self.ui.connect_btn.setToolTip(_("Connect with the printer"))
        self.ui.connect_btn.clicked.disconnect(self.disconnect)
        self.ui.connect_btn.clicked.connect(self.parent.connect_printer)

        msg = _("Disconnected.")
        self.logdisp(msg)
        self.parent.set_statusbar(msg)

    def layer_change_cb(self, newlayer):
        """Callback when the printed layer changed"""
        pronsole.pronsole.layer_change_cb(self, newlayer)
        if self.settings.mainviz != "3D" or self.settings.trackcurrentlayer3d:
            wx.CallAfter(self.gviz.setlayer, newlayer)

    def update_tempdisplay(self):
        try:
            temps = parse_temperature_report(self.tempreadings)
            if "T0" in temps and temps["T0"][0]:
                hotend_temp = float(temps["T0"][0])
            elif "T" in temps and temps["T"][0]:
                hotend_temp = float(temps["T"][0])
            else:
                hotend_temp = None
            if hotend_temp is not None:
                # if self.display_graph: wx.CallAfter(self.graph.SetExtruder0Temperature, hotend_temp)
                # if self.display_gauges: wx.CallAfter(self.hottgauge.SetValue, hotend_temp)
                if self.display_gauges:
                    self.guisignals.set_printtemp_value.emit(hotend_temp)
                setpoint = None
                if "T0" in temps and temps["T0"][1]: setpoint = float(temps["T0"][1])
                elif temps["T"][1]: setpoint = float(temps["T"][1])
                if setpoint is not None:
                    # if self.display_graph: wx.CallAfter(self.graph.SetExtruder0TargetTemperature, setpoint)
                    # if self.display_gauges: wx.CallAfter(self.hottgauge.SetTarget, setpoint)
                    if self.display_gauges:
                        self.guisignals.set_printtemp_target.emit(setpoint)
            if "T1" in temps:
                hotend_temp = float(temps["T1"][0])
                # if self.display_graph: wx.CallAfter(self.graph.SetExtruder1Temperature, hotend_temp)
                setpoint = temps["T1"][1]
                # if setpoint and self.display_graph:
                #     wx.CallAfter(self.graph.SetExtruder1TargetTemperature, float(setpoint))
            bed_temp = float(temps["B"][0]) if "B" in temps and temps["B"][0] else None
            if bed_temp is not None:
                # if self.display_graph: wx.CallAfter(self.graph.SetBedTemperature, bed_temp)
                # if self.display_gauges: wx.CallAfter(self.bedtgauge.SetValue, bed_temp)
                if self.display_gauges:
                    self.guisignals.set_bedtemp_value.emit(bed_temp)
                setpoint = temps["B"][1]
                if setpoint:
                    setpoint = float(setpoint)
                    # if self.display_graph: wx.CallAfter(self.graph.SetBedTargetTemperature, setpoint)
                    # if self.display_gauges: wx.CallAfter(self.bedtgauge.SetTarget, setpoint)
                    if self.display_gauges:
                        self.guisignals.set_bedtemp_target.emit(setpoint)
        except:
            traceback.print_exc()

    def update_pos(self):
        bits = gcoder.m114_exp.findall(self.posreport)
        x = None
        y = None
        z = None
        for bit in bits:
            if not bit[0]: continue
            if x is None and bit[0] == "X":
                x = float(bit[1])
            elif y is None and bit[0] == "Y":
                y = float(bit[1])
            elif z is None and bit[0] == "Z":
                z = float(bit[1])
        if x is not None: self.current_pos[0] = x
        if y is not None: self.current_pos[1] = y
        if z is not None: self.current_pos[2] = z

    @QtCore.Slot(str)
    def recvcb(self, l):
        report_type = self.recvcb_report(l)
        isreport = report_type != REPORT_NONE
        if report_type == REPORT_POS:
            self.update_pos()
        elif report_type == REPORT_TEMP:
            # wx.CallAfter(self.tempdisp.SetLabel, self.tempreadings.strip().replace("ok ", ""))
            self.update_tempdisplay()
        tstring = l.rstrip()
        if not self.p.loud and (tstring not in ["ok", "wait"] and not isreport):
            self.guisignals.addtext.emit(tstring + "\n")
        for listener in self.recvlisteners:
            listener(l)

    def parseusercmd(self, line):
        if line.upper().startswith("M114"):
            self.userm114 += 1
        elif line.upper().startswith("M105"):
            self.userm105 += 1

    def sendline(self):
        command = self.ui.commandbox.text()
        if not len(command):
            return
        self.guisignals.addtext.emit(">>> " + command + "\n")
        self.parseusercmd(str(command))
        self.onecmd(str(command))
        self.ui.commandbox.setText(u'')
        self.ui.commandbox.history.append(command)
        self.ui.commandbox.histindex = len(self.ui.commandbox.history)

    def cbkey_action(self, val):
        hist_len = len(self.ui.commandbox.history)
        # if self.ui.commandbox.text():
        #     # save current command
        #     self.ui.commandbox.history.append(self.ui.commandbox.text())
        if hist_len:
            self.ui.commandbox.histindex = (self.ui.commandbox.histindex + \
                    val) % hist_len
            self.ui.commandbox.setText(
                    self.ui.commandbox.history[self.ui.commandbox.histindex]
                    )
            self.ui.commandbox.selectAll()
        
    def cbkey(self, code):
        if code == QtCore.Qt.Key_Up:
            self.cbkey_action(-1)
        elif code == QtCore.Qt.Key_Down:
            self.cbkey_action(1)

    def clamped_move_message(self):
        self.logdisp(_("Manual move outside of the build volume prevented (see the \"Clamp manual moves\" option)."))

    def printfile(self, gcode):
        self.extra_print_time = 0
        if self.paused:
            self.p.paused = 0
            self.paused = 0
            if self.sdprinting:
                self.p.send_now("M26 S0")
                self.p.send_now("M24")
                return

        if not gcode:
            self.parent.set_statusbar(_("No file loaded. Please use load first."))
            return

        if not self.p.online:
            self.parent.set_statusbar(_("Not connected to printer."))
            return

        if not self.fgcode:
            self.parent.set_statusbar(_("No file loaded. Please use load first."))
            return

        self.p.startprint(self.fgcode)

    def do_settemp(self, l, command, msg):
        if isinstance(l, str) or isinstance(l, unicode):
            l = l.replace(", ", ".")
        f = float(l)
        if f >= 0:
            if self.p.online:
                self.p.send_now(command)
                self.guisignals.addtext.emit(msg % f)
                self.sethotendgui(f)
            else:
                self.guisignals.addtext.emit(_("Printer is not online."))
        else:
            self.guisignals.addtext.emit(
                _("You cannot set negative temperatures. " \
                  "To turn the hotend off entirely, set its temperature to 0."))

    def set_printtemp(self, l):
        command = "M104 S" + l
        msg = _("Setting hotend temperature to %f degrees Celsius.")
        self.do_settemp(l, command, msg)

    def set_bedtemp(self, l):
        command = "M140 S" + l
        msg = _("Setting bed temperature to %f degrees Celsius.")
        self.do_settemp(l, command, msg)

    def sethotendgui(self, f):
        self.hsetpoint = f
        if self.display_gauges:
            self.guisignals.set_printtemp_target.emit(float(f))
        # if self.display_graph: wx.CallAfter(self.graph.SetExtruder0TargetTemperature, int(f))
        if f > 0:
            self.guisignals.set_printtemp_value.emit(float(f))
        #     self.set("last_temperature", str(f))
        #     wx.CallAfter(self.settoff.SetBackgroundColour, None)
        #     wx.CallAfter(self.settoff.SetForegroundColour, None)
        #     wx.CallAfter(self.settbtn.SetBackgroundColour, "#FFAA66")
        #     wx.CallAfter(self.settbtn.SetForegroundColour, "#660000")
        #     wx.CallAfter(self.htemp.SetBackgroundColour, "#FFDABB")
        # else:
        #     wx.CallAfter(self.settoff.SetBackgroundColour, "#0044CC")
        #     wx.CallAfter(self.settoff.SetForegroundColour, "white")
        #     wx.CallAfter(self.settbtn.SetBackgroundColour, None)
        #     wx.CallAfter(self.settbtn.SetForegroundColour, None)
        #     wx.CallAfter(self.htemp.SetBackgroundColour, "white")
        #     wx.CallAfter(self.htemp.Refresh)
