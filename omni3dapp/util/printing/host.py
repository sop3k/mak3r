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
try: import simplejson as json
except ImportError: import json

if os.name == "nt":
    try:
        import _winreg
    except:
        pass

from PySide import QtCore, QtGui

from serial import SerialException
from .utils import dosify, \
    iconfile, configfile, format_time, format_duration, \
    hexcolor_to_float, parse_temperature_report, \
    prepare_command, check_rgb_color, check_rgba_color

from omni3dapp.util import profile
from omni3dapp.util.printing.pronsole import Pronsole
from omni3dapp.util.printing import gcoder
from .pronsole import REPORT_NONE, REPORT_POS, REPORT_TEMP
from omni3dapp.logger import log


class PrintingSignals(QtCore.QObject):
    connect_to_port_sig = QtCore.Signal()


class GuiSignals(QtCore.QObject):
    addtext = QtCore.Signal(str)
    setonline = QtCore.Signal()
    setoffline = QtCore.Signal()
    enable_printing = QtCore.Signal()
    set_statusbar = QtCore.Signal(str)
    set_printtemp_target = QtCore.Signal(float)
    set_bedtemp_target = QtCore.Signal(float)
    set_printtemp_value = QtCore.Signal(float)
    set_bedtemp_value = QtCore.Signal(float)
    set_extr0temp_target = QtCore.Signal(float)
    # set_tempprogress_value = QtCore.Signal(float, float)


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

    def _get_display_graph(self):
        # return self.settings.tempgraph
        return True
    display_graph = property(_get_display_graph)

    def _get_display_gauges(self):
        # return self.settings.tempgauges
        return True
    display_gauges = property(_get_display_gauges)

    def __init__(self, parent):
        Pronsole.__init__(self, parent)
        self.parent = parent
        self.paused = False
        self.sdprinting = False
        self.heating = False
        self.heating_paused = False
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

        self.custombuttons = []
        self.btndict = {}
        self.filehistory = None
        self.autoconnect = profile.settingsDictionary.get('auto_connect').getValue()
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

        self.parent.setStatusbar(_("Not connected to printer"))
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

        printset = set(string.printable)
        self.is_printable = lambda text: set(text).issubset(printset)
        self.checked_baudrate = set()
        self.checked_ports = set()

        self.guisignals = GuiSignals()
        self.guisignals.addtext.connect(self.addtexttolog)
        self.guisignals.setonline.connect(self.online_gui) 
        self.guisignals.setoffline.connect(self.offline_gui) 
        self.guisignals.enable_printing.connect(
            self.parent.sceneview.enablePrinting)
        self.guisignals.set_statusbar.connect(self.parent.setStatusbar)
        self.guisignals.set_printtemp_target.connect(
            self.parent.sceneview.setPrinttempTarget)
        self.guisignals.set_bedtemp_target.connect(
            self.parent.sceneview.setBedtempTarget)
        self.guisignals.set_printtemp_value.connect(
            self.parent.sceneview.setPrinttempValue)
        self.guisignals.set_bedtemp_value.connect(
            self.parent.sceneview.setBedtempValue)
        self.guisignals.set_extr0temp_target.connect(
            self.parent.sceneview.setExtr0TempTarget)
        # self.guisignals.set_tempprogress_value.connect(
        #     self.parent.sceneview.setTempProgress)

        if self.autoconnect:
            self.start_connect_thread()

    def setpaused(self, paused):
        self.p.paused = 0
        self.p.printing = 0
        self.paused = 0

    def start_connect_thread(self):
        self.finish_connector()

        self.connect_thread = QtCore.QThread(self.parent) 
        self.connector = Connector(self, self.p)
        self.connector.moveToThread(self.connect_thread)

        self.connect_thread.started.connect(self.connector.connect_printer)
        self.connector.set_statusbar_sig.connect(self.parent.setStatusbar)
        self.connector.set_disconnected_sig.connect(self.parent.setDisconnected) 
        self.connector.start_listener_sig.connect(self.p.start_listener)
        self.connector.set_online_sig.connect(self.set_online)
        self.printingsignals = PrintingSignals()
        self.printingsignals.connect_to_port_sig.connect(self.connector.connect_to_port)

        self.connector.finished.connect(self.connect_thread.quit)
        self.connector.finished.connect(self.connector.deleteLater)
        self.connect_thread.finished.connect(self.connect_thread.deleteLater)

        self.parent.setStatusbar(_("Trying to connect to printer..."))
        self.connect_thread.start()

    @QtCore.Slot(str)
    def set_online(self, msg):
        self.online(msg)
        self.after_connect()
        self.parent.setConnected()

    @QtCore.Slot()
    def finish_connector(self):
        self.printingsignals = None
        if hasattr(self, "connect_thread"):
            try:
                self.connect_thread.terminate()
            except Exception as e:
                log.error(e)
            finally:
                self.connect_thread = None

    def terminate_printing_threads(self):
        pass

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
        self.parent.setStatusbar(_("Disconnecting from printer..."))
        if self.heating:
            self.pause()

        if self.p.printing or self.p.paused or self.paused:
            log.debug("Disconnecting while printing")
            self.store_predisconnect_state()
        self.p.signals.disconnect_sig.emit()
        self.statuscheck = False
        if self.status_thread:
            try:
                self.status_thread.terminate()
            except Exception as e:
                log.error(e)
            finally:
                self.status_thread = None

        if self.paused:
            self.p.paused = 0
            self.p.printing = 0
            self.paused = 0
            if self.sdprinting:
                self.p.send_now("M26 S0")

        self.guisignals.setoffline.emit()

    @QtCore.Slot(str)
    def addtexttolog(self, text, command=False):
        if self.is_printable(text):
            if not text.endswith("\n"):
                text += "\n"
            self.parent.addToLogbox(text)
            if not command:
                log.debug(text)
        else:
            msg = _("Attempted to write invalid text to console, which could be due to an invalid baudrate. Reconnecting...")
            log.debug(msg)
            if getattr(self, 'connector'):
                self.printingsignals.connect_to_port_sig.emit() 

    def sentcb(self, line, gline):
        """Callback when a printer gcode has been sent"""
        if not gline:
            pass
        elif gline.command in ["M104", "M109"]:
            gline_s = gcoder.S(gline)
            if gline_s is not None:
                temp = gline_s
                if self.display_gauges:
                    # self.hottgauge.setTarget(temp)
                    self.guisignals.set_printtemp_target.emit(temp)
                if self.display_graph:
                    # wx.CallAfter(self.graph.SetExtruder0TargetTemperature, temp)
                    self.guisignals.set_extr0temp_target.emit(temp)
        elif gline.command in ["M140", "M190"]:
            gline_s = gcoder.S(gline)
            if gline_s is not None:
                temp = gline_s
                if self.display_gauges:
                    # self.bedtgauge.SetTarget(temp)
                    self.guisignals.set_bedtemp_target.emit(temp)
                # if self.display_graph:
                #     self.graph.SetBedTargetTemperature(temp)
                #     self.guisignals.set_graphbedtemp_target.emit(temp)
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
        pass
        # if gline.is_move:
        #     print "should set current gline here"

        # if gline.is_move:
        #     if hasattr(self.gwindow, "set_current_gline"):
        #         wx.CallAfter(self.gwindow.set_current_gline, gline)
        #     if hasattr(self.gviz, "set_current_gline"):
        #         wx.CallAfter(self.gviz.set_current_gline, gline)

    # def startcb(self, resuming=False):
    #     """Callback on print start"""
    #     Pronsole.startcb(self, resuming)
    #     # TODO: locking interface dependent on settings
    #     # if self.settings.lockbox and self.settings.lockonstart:
    #     #     wx.CallAfter(self.lock, force = True)

    @QtCore.Slot(bool)
    def endcb(self):
        """Callback on print end/pause"""
        Pronsole.endcb(self)
        if self.p.queueindex == 0:
            self.p.runSmallScript(self.endScript)
            self.parent.sceneview.onEndprint()

    def move_axis(self, axis, curr_pos, step, mach_size):
        # self.zb.clearRepeat()
        if step == 0:
            return
        offset = profile.getMachineSettingFloat('machine_{0}_offset'.format(axis))
        # if self.settings.clamp_jogging:
        new_pos = curr_pos + step
        # if new_x < x_offset or new_x > mach_width + x_offset:
        if new_pos > mach_size + offset or new_pos < 0:
            self.clamped_move_message()
            return
        self.onecmd('move {0} {1}'.format(axis.upper(), step))
        self.p.send_now('M114')

    def move_x(self, step, mach_width):
        self.move_axis('x', self.current_pos[0], step, mach_width)

    def move_y(self, step, mach_depth):
        self.move_axis('y', self.current_pos[1], step, mach_depth)

    def move_z(self, step, mach_height):
        self.move_axis('z', self.current_pos[2], step, mach_height)

    def home_position(self, axis):
        if axis == 'all':
            self.onecmd('home')
        self.onecmd('home {0}'.format(axis.upper()))
        self.p.send_now('M114')

    def statuschecker(self):
        Pronsole.statuschecker(self)
        self.parent.setStatusbar(_("Not connected to printer"))

    def pause(self):
        if self.paused:
            self.parent.setStatusbar(_("Already paused"))
            return

        msg =_("Pausing print at: {}".format(format_time(time.time())))
        self.parent.setStatusbar(msg)

        if self.heating:
            self.heater.finished.emit()
            self.p.send_now("M104 S0")
            self.p.send_now("M140 S0")
            self.heating_paused = True
            self.paused = True
            self.heating_finished()
            self.parent.setStatusbar(_("Heating paused"))
            return

        if self.sdprinting:
            self.p.send_now("M25")
        else:
            if not self.p.printing:
                self.parent.setStatusbar(_("Not printing"))
                return
            self.p.pause()
            self.p.runSmallScript(self.pauseScript)
        self.paused = True
        # self.p.runSmallScript(self.pauseScript)
        self.extra_print_time += int(time.time() - self.starttime)

    def resume(self):
        self.log(_("Resuming"))
        self.paused = False

        if self.heating_paused:
            self.heating_paused = False
            self.start_heating()
            return

        if self.sdprinting:
            self.p.send_now("M24")
        else:
            self.p.resume()

    def recover(self, event):
        self.extra_print_time = 0
        if not self.p.online:
            self.parent.setStatusbar(_("Not connected to printer"))
            return
        # Reset Z
        self.p.send_now("G92 Z%f" % self.predisconnect_layer)
        # Home X and Y
        self.p.send_now("G28 X Y")
        self.on_startprint()
        self.p.startprint(self.predisconnect_mainqueue, self.p.queueindex)

    def reset(self, event):
        self.log(_("Reset."))
        print "Resetting the printer - should ask if user is sure to reset it"
        # dlg = wx.MessageDialog(self, _("Are you sure you want to reset the printer?"), _("Reset?"), wx.YES | wx.NO)
        # if dlg.ShowModal() == wx.ID_YES:
        #     self.p.reset()
        #     self.sethotendgui(0)
        #     self.setbedgui(0)
        #     self.p.printing = 0
        #     wx.CallAfter(self.printbtn.SetLabel, _("Print"))
        #     if self.paused:
        #         self.p.paused = 0
        #         wx.CallAfter(self.pausebtn.SetLabel, _("Pause"))
        #         self.paused = 0
        #     wx.CallAfter(self.toolbarsizer.Layout)
        # dlg.Destroy()

    def process_host_command(self, command):
        """Override host command handling"""
        command = command.lstrip()
        if command.startswith(";@pause"):
            self.pause(None)
        else:
            Pronsole.process_host_command(self, command)

    def online(self):
        """Callback when printer goes online"""
        msg = _("Printer is now online.")
        self.log(msg)
        self.addtexttolog(msg)
        self.online_gui()
        self.parent.sceneview.enablePrinting()

    @QtCore.Slot()
    def online_gui(self):
        """Callback when printer goes online (graphical bits)"""
        self.parent.setConnected()

    @QtCore.Slot()
    def offline_gui(self):
        self.parent.setDisconnected()

        msg = _("Disconnected.")
        self.logdisp(msg)

    def layer_change_cb(self, newlayer):
        """Callback when the printed layer changed"""
        Pronsole.layer_change_cb(self, newlayer)
        # if self.settings.mainviz != "3D" or self.settings.trackcurrentlayer3d:
        print "should set a layer in gviz here"
            # wx.CallAfter(self.gviz.setlayer, newlayer)

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
                if self.display_gauges:
                    self.guisignals.set_printtemp_value.emit(hotend_temp)
                setpoint = None
                if "T0" in temps and temps["T0"][1]: setpoint = float(temps["T0"][1])
                elif temps["T"][1]: setpoint = float(temps["T"][1])
                if setpoint is not None:
                    if self.display_gauges:
                        # self.guisignals.set_printtemp_target.emit(setpoint)
                        self.parent.sceneview.setPrinttempTarget(setpoint)
            if "T1" in temps:
                hotend_temp = float(temps["T1"][0])
                # if self.display_graph: wx.CallAfter(self.graph.SetExtruder1Temperature, hotend_temp)
                setpoint = temps["T1"][1]
                # if setpoint and self.display_graph:
                #     wx.CallAfter(self.graph.SetExtruder1TargetTemperature, float(setpoint))
            bed_temp = float(temps["B"][0]) if "B" in temps and temps["B"][0] else None
            if bed_temp is not None:
                if self.display_gauges:
                    self.guisignals.set_bedtemp_value.emit(bed_temp)
                setpoint = temps["B"][1]
                if setpoint:
                    setpoint = float(setpoint)
                    if self.display_gauges:
                        # self.guisignals.set_bedtemp_target.emit(setpoint)
                        self.parent.sceneview.setBedtempTarget(setpoint)

            # self.guisignals.set_tempprogress_value.emit(hotend_temp, bed_temp)
            self.parent.sceneview.setTempProgress(hotend_temp, bed_temp)
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
            # self.guisignals.addtext.emit(tstring + "\n")
            self.addtexttolog(tstring + "\n")
        for listener in self.recvlisteners:
            listener(l)

    def parseusercmd(self, line):
        if line.upper().startswith("M114"):
            self.userm114 += 1
        elif line.upper().startswith("M105"):
            self.userm105 += 1

    def sendline(self, command):
        if not len(command):
            return
        self.addtexttolog(">>> {0}\n".format(command), command=True)
        self.parseusercmd(str(command))
        self.onecmd(str(command))

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

        if not gcode or not (self.fgcode is not None and self.fgcode.lines):
            self.parent.setStatusbar(_("No file loaded. Please use load first"))
            return

        if not self.p.online:
            self.parent.setStatusbar(_("Not connected to printer"))
            return

        # Heat up the bed and extruders
        self.start_heating()

    def startprint(self):
        log.debug("Starting print")
        ret = self.p.startprint(self.fgcode)
        if not ret:
            self.parent.setStatusbar(_("Printing failed to start"))

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

    def set_printtemp(self, l):
        command = "M104 S{}".format(l)
        msg = _("Setting nozzle temperature to {} degrees Celsius.")
        self.do_settemp(l, command, msg)

    def set_bedtemp(self, l):
        command = "M140 S{}".format(l)
        msg = _("Setting bed temperature to {} degrees Celsius.")
        self.do_settemp(l, command, msg)

    def do_settemp(self, l, command, msg):
        if isinstance(l, str) or isinstance(l, unicode):
            l = l.replace(", ", ".")
        f = float(l)
        if f >= 0:
            if self.p.online:
                self.p.send_now(command)
                self.guisignals.addtext.emit(msg.format(f))
                self.guisignals.set_statusbar.emit(msg.format(f))
                # self.sethotendgui(f)
            else:
                self.guisignals.addtext.emit(_("Printer is not online."))
        else:
            self.guisignals.addtext.emit(
                _("You cannot set negative temperatures. " \
                  "To turn the hotend off entirely, set its temperature to 0."))

    def set_heating_started(self):
        self.heating = True
        self.parent.sceneview.setHeatingStarted()

    def heating_finished(self):
        log.debug("Setting heating finished; about to start printing")
        self.heater.finished.emit()
        self.heating = False
        if not self.paused:
            self.startprint()

    def start_heating(self):
        self.heating_thread = QtCore.QThread(self.parent)
        self.heater = Heater(self.p, self.set_printtemp, self.set_bedtemp)
        self.heater.moveToThread(self.heating_thread)

        self.heating_thread.started.connect(self.heater.heat_up)
        self.heater.set_progress_sig.connect(self.parent.setProgress)

        self.heater.finished.connect(self.heating_thread.quit)
        self.heater.finished.connect(self.heater.deleteLater)
        self.heating_thread.finished.connect(self.heating_thread.deleteLater)

        self.parent.setStatusbar(_("Heating up..."))
        self.heating_thread.start()

        self.set_heating_started()


class Heater(QtCore.QObject):
    set_progress_sig = QtCore.Signal(float)
    finished = QtCore.Signal()

    def __init__(self, printcore, set_printtemp_func, set_bedtemp_func):
        super(Heater, self).__init__()
        self.p = printcore
        self.set_printtemp = set_printtemp_func
        self.set_bedtemp = set_bedtemp_func

    def heat_up(self):
        self.set_progress_sig.emit(0.01)
        printtemp = profile.settingsDictionary.get("print_temperature")
        if printtemp:
            self.set_printtemp(printtemp.getValue())

        bedtemp = profile.settingsDictionary.get("print_bed_temperature")
        if bedtemp:
            self.set_bedtemp(bedtemp.getValue())


class Connector(QtCore.QObject):
    set_statusbar_sig = QtCore.Signal(str)
    set_disconnected_sig = QtCore.Signal(str)
    set_online_sig = QtCore.Signal(str)
    start_listener_sig = QtCore.Signal()
    finished = QtCore.Signal()

    def __init__(self, parent, pcore):
        super(Connector, self).__init__()
        self.parent = parent
        self.pcore = pcore

    def connect_printer(self):
        self.ports = self.rescanports()
        if not self.ports:
            self.set_statusbar_sig.emit(_('Could not find active ports'))
            self.finished.emit()
            return

        try:
            port_val = profile.settingsDictionary.get('port_type').getValue()
            baud_val = profile.settingsDictionary.get(
                'port_baud_rate').getValue()
            if port_val and baud_val:
                self.connect_port_baud(port_val, int(baud_val))
            else:
                self.connect_to_port()
        except Exception as e:
            log.debug("Error getting port and baud settings from profile: {}".format(e))
            self.connect_to_port()

    def connect_port_baud(self, port_val, baud_val):
        msg = "Connecting to port {0} at baudrate {1}".format(port_val,
            baud_val)
        self.set_statusbar_sig.emit(msg)

        if self.parent.paused:
            self.parent.setpaused(0)
            if self.parent.sdprinting:
                self.pcore.send_now("M26 S0")

        ret = self.pcore.connect(port_val, baud_val)
        if not ret:
            self.connect_to_port()
        else:
            print "Calling start listener"
            self.start_listener_sig.emit()

    @QtCore.Slot()
    def connect_to_port(self):
        print "inside connect to port"
        if not hasattr(self, 'ports') or not self.ports:
            msg = _("Could not connect to printer")
            # self.set_statusbar_sig.emit(msg)
            # log.error("{}; scanned every port at every baudrate".format(msg))
            self.set_disconnected_sig.emit(msg)
            return

        if not hasattr(self, 'baud_set') or not self.baud_set:
            print "Getting new port value"

            self.port_val = self.ports.pop()
            try:
                self.baud_set = profile.settingsDictionary.get(
                    'port_baud_rate').getOptions()
            except Exception as e:
                log.error(e)
                self.baud_set = []
            if not self.baud_set:
                self.baud_set = [250000]
            log.debug("New baud set is: {}".format(self.baud_set))

        self.baud_val = self.baud_set.pop()
        try:
            self.baud_val = int(self.baud_val)
        except ValueError as e:
            log.error(_("Could not parse baud rate: {0}".format(e)))
            return self.connect_to_port()

        return self.connect_port_baud(self.port_val, self.baud_val)

    def set_connected(self):
        try:
            settings_port = profile.settingsDictionary.get('port_type').getValue()
        except AttributeError:
            settings_port = ""
        if self.port_val != settings_port:
            profile.putMachineSetting('port_type', self.port_val)

        try:
            settings_baud = profile.settingsDictionary.get('port_baud_rate').getValue()
        except AttributeError:
            settings_baud = ""
        if self.baud_val != settings_baud:
            profile.putMachineSetting('port_baud_rate', self.baud_val)
        msg = _("Connected to port {0} at baudrate {1}".format(
            self.port_val, self.baud_val))

        self.set_online_sig.emit(msg)

        # if self.predisconnect_mainqueue:
        #     self.recoverbtn.Enable()

    def rescanports(self):
        scanned = self.scanserial()
        portslist = list(scanned)
        log.debug("Portlist: {}".format(portslist))
        port = profile.settingsDictionary.get('port_type') or ""
        if port:
            port = port.getValue()
        if port != "" and port not in portslist:
            portslist.append(port)
        if portslist:    
            self.set_statusbar_sig.emit(_("Found active ports"))
        else:
            self.set_statusbar_sig.emit(_("Did not find any connected ports"))

        return portslist

    def scanserial(self):
        """scan for available ports. return a list of device names."""
        baselist = []
        if os.name == "nt":
            try:
                log.debug("Getting registry key: {}".format(
                    _winreg.HKEY_LOCAL_MACHINE))
                key = _winreg.OpenKey(
                    _winreg.HKEY_LOCAL_MACHINE,
                    "HARDWARE\\DEVICEMAP\\SERIALCOMM")
                log.debug("Got key: {}".format(key))
                i = 0
                while(1):
                    baselist += [_winreg.EnumValue(key, i)[1]]
                    i += 1
                log.debug("Baselist is: {}".format(baselist))
            except Exception as e:
                log.error("Error opening windows registry key: {}".format(e))

        for g in ['/dev/ttyUSB*', '/dev/ttyACM*', "/dev/tty.*", "/dev/cu.*", "/dev/rfcomm*"]:
            baselist += glob.glob(g)
        log.debug("Baselist is: {}".format(baselist))
        return filter(self._bluetoothSerialFilter, baselist)

    def _bluetoothSerialFilter(self, serial):
        return not ("Bluetooth" in serial or "FireFly" in serial)
