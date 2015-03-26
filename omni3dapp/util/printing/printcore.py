#!/usr/bin/env python

# This file is part of the Printrun suite.
#
# Printrun is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Printrun is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Printrun.  If not, see <http://www.gnu.org/licenses/>.

__version__ = "2014.08.01"

from serial import Serial, SerialException
from select import error as SelectError
from Queue import Queue, Empty as QueueEmpty
import time
import platform
import os
import sys
reload(sys).setdefaultencoding('utf8')
import traceback
import errno
import socket
import re
from functools import wraps
from collections import deque
from PySide import QtCore

from . import gcoder
from .utils import install_locale, decode_utf8

from omni3dapp.logger import log


def control_ttyhup(port, disable_hup):
    """Controls the HUPCL"""
    if platform.system() == "Linux":
        if disable_hup:
            os.system("stty -F %s -hup" % port)
        else:
            os.system("stty -F %s hup" % port)


def enable_hup(port):
    control_ttyhup(port, False)


def disable_hup(port):
    control_ttyhup(port, True)


class ConnectionSignals(QtCore.QObject):
    connect_sig = QtCore.Signal(str, int)
    disconnect_sig = QtCore.Signal()


class Printcore(QtCore.QObject):
    def __init__(self, parent=None, host=None, port=None, baud=None):
        """Initializes a printcore instance. Pass the port and baud rate to
           connect immediately"""
        super(Printcore, self).__init__()
        self.parent = parent
        self.host = host
        self.analyzer = gcoder.GCode()
        self.printer = None
        self.printer_tcp = None
        # Serial instance connected to the printer, should be None when
        # disconnected
        # clear to send, enabled after responses
        # FIXME: should probably be changed to a sliding window approach
        self.clear = 0
        # The printer has responded to the initial command and is active
        self.online = False
        # is a print currently running, true if printing, false if paused
        self.printing = False
        self.mainqueue = None
        self.priqueue = Queue(0)
        self.queueindex = 0
        self.lineno = 0
        self.resendfrom = -1
        self.paused = False
        self.sentlines = {}
        self.log = deque(maxlen = 10000)
        self.sent = []
        self.writefailures = 0
        self.tempcb = None  # impl (wholeline)
        self.recvcb = None  # impl (wholeline)
        self.sendcb = None  # impl (wholeline)
        self.preprintsendcb = None  # impl (wholeline)
        self.printsendcb = None  # impl (wholeline)
        self.layerchangecb = None  # impl (wholeline)
        self.errorcb = None  # impl (wholeline)
        self.startcb = None  # impl ()
        self.endcb = None  # impl ()
        self.onlinecb = None  # impl ()
        self.loud = False  # emit sent and received lines to terminal
        self.tcp_streaming_mode = False
        self.wait = 0  # default wait period for send(), send_now()
        self.read_thread = None
        self.stop_read_thread = False
        self.send_thread = None
        self.stop_send_thread = False
        self.print_thread = None

        self.signals = ConnectionSignals()
        self.signals.connect_sig.connect(self.connect)
        self.signals.disconnect_sig.connect(self.disconnect)

        # if port is not None and baud is not None:
        #     self.signals.connect_sig.emit({'port': port, 'baud': baud})
        self.xy_feedrate = None
        self.z_feedrate = None

    def logError(self, error):
        if self.errorcb:
            try: self.errorcb(error)
            except: traceback.print_exc()
        else:
            log.error(error)

    @QtCore.Slot()
    def disconnect(self):
        """Disconnects from printer and pauses the print
        """
        if not self.printer:
            if self.read_thread:
                self.stop_read_thread = True
                try:
                    self.read_thread.terminate()
                except Exception as e:
                    log.error(e)
                self.read_thread = None

            if self.print_thread:
                self.printing = False
                try:
                    self.print_thread.terminate()
                except Exception as e:
                    log.error(e)
                self.print_thread = None
            self._stop_sender()
            try:
                self.printer.close()
            except socket.error, e:
                log.error(e)
            except OSError, e:
                log.error(e)

        self.printer = None
        self.online = False
        self.printing = False

    @QtCore.Slot(str, int)
    def connect(self, port, baud):
        """Set port and baudrate if given, then connect to printer
        """
        if self.printer:
            self.disconnect()
        if not (port and baud):
            return

        # Connect to socket if "port" is an IP, device if not
        host_regexp = re.compile("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$|^(([a-zA-Z0-9]|[a-zA-Z0-9][a-zA-Z0-9\-]*[a-zA-Z0-9])\.)*([A-Za-z0-9]|[A-Za-z0-9][A-Za-z0-9\-]*[A-Za-z0-9])$")
        is_serial = True
        if ":" in port:
            bits = port.split(":")
            if len(bits) == 2:
                hostname = bits[0]
                try:
                    port = int(bits[1])
                    if host_regexp.match(hostname) and 1 <= port <= 65535:
                        is_serial = False
                except:
                    pass
        self.writefailures = 0
        if not is_serial:
            self.printer_tcp = socket.socket(socket.AF_INET,
                                             socket.SOCK_STREAM)
            self.printer_tcp.settimeout(1.0)
            try:
                self.printer_tcp.connect((hostname, port))
                self.printer_tcp.settimeout(0.25)
                self.printer = self.printer_tcp.makefile()
            except socket.error as e:
                log.error(_("Could not connect to {0}:{1}: " \
                          "\nSocket error {2}: \n{3}").format(
                              hostname, port, e.errno, e.strerror))
                self.printer = None
                self.printer_tcp = None
                return
        else:
            disable_hup(port)
            self.printer_tcp = None
            try:
                self.printer = Serial(port=port,
                                      baudrate=baud,
                                      timeout=0.25)
            except Exception as e:
                log.error(_("Could not connect to {0} at baudrate {1}: " \
                    "\n{2} {3}").format(port, baud, type(e), e))
                self.printer = None
                return

        self.stop_read_thread = False
        self.listener = Listener(self)
        self.read_thread = QtCore.QThread(self.parent)
        self.listener.moveToThread(self.read_thread)

        self.read_thread.started.connect(self.listener.listen)
        self.listener.send_command.connect(self._send)
        self.listener.recvcb_sig.connect(self.recvcb)
        self.listener.set_online.connect(self.onlinecb)

        self.listener.finished.connect(self.read_thread.quit)
        self.listener.finished.connect(self.listener.deleteLater)
        self.read_thread.finished.connect(self.read_thread.deleteLater)

        self.read_thread.start()
        self._start_sender()

        self.host.after_connect()

        self.parent.setConnected()
        return True

    def reset(self):
        """Reset the printer
        """
        if self.printer and not self.printer_tcp:
            self.printer.setDTR(1)
            time.sleep(0.2)
            self.printer.setDTR(0)

    def _start_sender(self):
        log.debug("Starting sender")
        self.stop_send_thread = False
        self.sender_worker = Sender(self)
        self.send_thread = QtCore.QThread(self.parent)
        self.sender_worker.moveToThread(self.send_thread)

        self.send_thread.started.connect(self.sender_worker.sender)
        self.sender_worker.send_command.connect(self._send)
        self.sender_worker.finished.connect(self.send_thread.quit)
        self.sender_worker.finished.connect(self.sender_worker.deleteLater)
        self.send_thread.finished.connect(self.send_thread.deleteLater)

        print "starting sender thread"
        self.send_thread.start()

    def _stop_sender(self):
        log.debug("Stopping sender thread")
        if not self.send_thread:
            return

        self.stop_send_thread = True
        try:
            self.send_thread.terminate()
        except RuntimeError as e:
            log.error(e)
        finally:
            self.send_thread = None

    def _checksum(self, command):
        return reduce(lambda x, y: x ^ y, map(ord, command))

    @QtCore.Slot(bool)
    def emit_startcb(self, resuming):
        if self.startcb is not None:
            self.startcb(resuming)

    @QtCore.Slot()
    def emit_endcb(self):
        if self.endcb is not None:
            self.endcb()

    @QtCore.Slot(int)
    def emit_layerchangecb(self, layer):
        if self.layerchangecb is not None:
            self.layerchangecb(layer)

    @QtCore.Slot(str)
    def emit_printsendcb(self, line):
        if self.printsendcb is not None:
            self.printsendcb(line)

    def start_print_thread(self, resuming=False):
        self.printer_thread = QtCore.QThread(self.parent)
        self.printer_worker = Printer(self, resuming)
        self.printer_worker.moveToThread(self.printer_thread)

        self.printer_thread.started.connect(self.printer_worker._print)
        self.printer_worker.pause_sig.connect(self.pause)
        self.printer_worker.finished.connect(self.finish_printer_thread)

        self.printer_worker.finished.connect(self.printer_thread.quit)
        self.printer_worker.finished.connect(self.printer_worker.deleteLater)
        self.printer_thread.finished.connect(self.printer_thread.deleteLater)

        # self._stop_sender()
        log.debug("Starting print thread...")
        self.printer_thread.start()

    def startprint(self, gcode, startindex=0):
        """Start a print, gcode is an array of gcode commands.
        returns True on success, False if already printing.
        The print queue will be replaced with the contents of the data array,
        the next line will be set to 0 and the firmware notified. Printing
        will then start in a parallel thread.
        """
        log.debug("Starting print inside printcore")
        if self.printing or not self.online or not self.printer:
            log.debug("Failed to start printing; exiting. "
                      "Printing: {0}, online: {1}, printer: {2}".format(
                        self.printing, self.online, self.printer))
            return False
        self.queueindex = startindex
        self.mainqueue = gcode
        self.printing = True
        self.lineno = 0
        self.resendfrom = -1
        self._send("M110", -1, True)
        if not gcode or not gcode.lines:
            log.debug("Returning from startprint before starting print thread."
                      "Gcode: {0}, no of gcode.lines: {1}".format(gcode, len(gcode.lines)))
            return True
        self.clear = False
        resuming = (startindex != 0)
        log.debug("Starting print thread - resuming {0}".format(resuming))
        self.start_print_thread(resuming)
        return True

    def finish_printer_thread(self):
        print "finishing printer thread"
        # if not self.printer_thread:
        #     return
        # try:
        #     self.printer_thread.terminate()
        # except Exception, e:
        #     log.error(e)
        # finally:
        #     self.printer_thread = None
        self._start_sender()

    def cancelprint(self):
        self.pause()
        self.paused = False
        self.mainqueue = None
        self.clear = True

    # run a simple script if it exists, no multithreading
    def runSmallScript(self, filename):
        if filename is None: return
        f = None
        try:
            with open(filename) as f:
                for i in f:
                    l = i.replace("\n", "")
                    l = l[:l.find(";")]  # remove comments
                    self.send_now(l)
        except:
            pass

    @QtCore.Slot()
    def pause(self):
        """Pauses the print, saving the current position.
        """
        if not self.printing: return False
        self.paused = True
        self.printing = False

        # try joining the print thread: enclose it in try/except because we
        # might be calling it from the thread itself
        try:
            self.printer_thread.terminate()
        except RuntimeError, e:
            log.error(e)

        self.printer_thread = None

        # saves the status
        self.pauseX = self.analyzer.abs_x
        self.pauseY = self.analyzer.abs_y
        self.pauseZ = self.analyzer.abs_z
        self.pauseE = self.analyzer.abs_e
        self.pauseF = self.analyzer.current_f
        self.pauseRelative = self.analyzer.relative

    def resume(self):
        """Resumes a paused print.
        """
        if not self.paused: return False
        if self.paused:
            # restores the status
            self.send_now("G90")  # go to absolute coordinates

            xyFeedString = ""
            zFeedString = ""
            if self.xy_feedrate is not None:
                xyFeedString = " F" + str(self.xy_feedrate)
            if self.z_feedrate is not None:
                zFeedString = " F" + str(self.z_feedrate)

            self.send_now("G1 X%s Y%s%s" % (self.pauseX, self.pauseY,
                                            xyFeedString))
            self.send_now("G1 Z" + str(self.pauseZ) + zFeedString)
            self.send_now("G92 E" + str(self.pauseE))

            # go back to relative if needed
            if self.pauseRelative: self.send_now("G91")
            # reset old feed rate
            self.send_now("G1 F" + str(self.pauseF))

        self.paused = False
        self.printing = True
        self.start_print_thread(True)

    def send(self, command, wait=0):
        """Adds a command to the checksummed main command queue if printing, or
        sends the command immediately if not printing"""

        if self.online:
            if self.printing:
                self.mainqueue.append(command)
            else:
                self.priqueue.put_nowait(command)
        else:
            log.error(_("Not connected to printer"))

    def send_now(self, command, wait=0):
        """Sends a command to the printer ahead of the command queue, without a
        checksum"""
        if self.online:
            self.priqueue.put_nowait(command)
        else:
            log.error(_("Not connected to printer"))

    def _send(self, command, lineno=0, calcchecksum=False):
        # Only add checksums if over serial (tcp does the flow control itself)
        if calcchecksum and not self.printer_tcp:
            prefix = "N" + str(lineno) + " " + command
            command = prefix + "*" + str(self._checksum(prefix))
            if "M110" not in command:
                self.sentlines[lineno] = command
        if self.printer:
            self.sent.append(command)
            # run the command through the analyzer
            gline = None
            try:
                gline = self.analyzer.append(command, store = False)
            except:
                log.warning(_("Could not analyze command %s:") % command +
                                "\n" + traceback.format_exc())
            if self.loud:
                log.info("SENT: %s" % command)
            if self.sendcb:
                try: self.sendcb(command, gline)
                except: log.error(traceback.print_exc())
            try:
                self.printer.write(str(command + "\n"))
                if self.printer_tcp:
                    try:
                        self.printer.flush()
                    except socket.timeout:
                        pass
                self.writefailures = 0
            except socket.error as e:
                if e.errno is None:
                    log.error(_(u"Can't write to printer (disconnected ?):") +
                                  "\n" + traceback.format_exc())
                else:
                    log.error(_(u"Can't write to printer (disconnected?) (Socket error {0}): {1}").format(e.errno, decode_utf8(e.strerror)))
                self.writefailures += 1
            except SerialException as e:
                self.logError(_(u"Can't write to printer (disconnected?) (SerialException): {0}").format(decode_utf8(str(e))))
                self.writefailures += 1
            except RuntimeError as e:
                self.logError(_(u"Socket connection broken, disconnected. ({0}): {1}").format(e.errno, decode_utf8(e.strerror)))
                self.writefailures += 1


class Listener(QtCore.QObject):
    send_command = QtCore.Signal(dict)
    recvcb_sig = QtCore.Signal(str)
    set_online = QtCore.Signal()
    finished = QtCore.Signal()

    greetings = ['start', 'Grbl ']

    def __init__(self, parent):
        super(Listener, self).__init__()
        self.parent = parent

    def listen(self):
        """This function acts on messages from the firmware
        """
        self.parent.clear = True
        if not self.parent.printing:
            self._listen_until_online()
        while self._listen_can_continue():
            line = self._readline()
            if line is None:
                break
            if line.startswith('DEBUG_'):
                continue
            if line.startswith(tuple(self.greetings)) or line.startswith('ok'):
                self.parent.clear = True
            if line.startswith('ok') and "T:" in line and self.parent.tempcb:
                # callback for temp, status, whatever
                # TODO
                try:
                    self.tempcb(line)
                except:
                    log.error(traceback.print_exc())
            elif line.startswith('Error'):
                log.error(line)
            # Teststrings for resend parsing       # Firmware     exp. result
            # line="rs N2 Expected checksum 67"    # Teacup       2
            if line.lower().startswith("resend") or line.startswith("rs"):
                for haystack in ["N:", "N", ":"]:
                    line = line.replace(haystack, " ")
                linewords = line.split()
                while len(linewords) != 0:
                    try:
                        toresend = int(linewords.pop(0))
                        self.parent.resendfrom = toresend
                        break
                    except:
                        pass
                self.parent.clear = True
        self.parent.clear = True
        self.finished.emit()

    def _listen_until_online(self):
        while not self.parent.online and self._listen_can_continue():
            self.parent._send("M105")
            if self.parent.writefailures >= 4:
                log.error(
                    _("Aborting connection attempt after 4 failed writes."))
                return
            empty_lines = 0
            while self._listen_can_continue():
                line = self._readline()
                if line is None: 
                    break  # connection problem
                # workaround cases where M105 was sent before printer Serial
                # was online an empty line means read timeout was reached,
                # meaning no data was received thus we count those empty lines,
                # and once we have seen 15 in a row, we just break and send a
                # new M105
                # 15 was chosen based on the fact that it gives enough time for
                # Gen7 bootloader to time out, and that the non received M105
                # issues should be quite rare so we can wait for a long time
                # before resending
                if not line:
                    empty_lines += 1
                    if empty_lines == 15: break
                else: empty_lines = 0
                if line.startswith(tuple(self.greetings)) \
                   or line.startswith('ok') or "T:" in line:
                    self.parent.online = True
                    if self.parent.onlinecb:
                        try: 
                            # self.parent.onlinecb()
                            self.set_online.emit()
                        except:
                            log.error(traceback.print_exc())
                    return

    def _listen_can_continue(self):
        if self.parent.printer_tcp:
            return not self.parent.stop_read_thread and self.parent.printer
        return (not self.parent.stop_read_thread
                and self.parent.printer
                and self.parent.printer.isOpen())

    def _readline(self):
        try:
            try:
                line = self.parent.printer.readline()
                if self.parent.printer_tcp and not line:
                    raise OSError(-1, "Read EOF from socket")
            except socket.timeout:
                return ""

            if len(line) > 1:
                self.parent.log.append(line)
                # if self.parent.recvcb:
                #     try: 
                #         # self.recvcb_sig.emit(line)
                #         self.parent.recvcb(line)
                #     except: 
                #         log.error(traceback.print_exc())
                self.recvcb_sig.emit(line)
                if self.parent.loud:
                    log.info("RECV: %s" % line.rstrip())
            return line
        except SelectError as e:
            if e.args[0] == 4:
                return None
            if 'Bad file descriptor' in e.args[1]:
                log.error(_(u"Can't read from printer " + \
                        "(disconnected?) (SelectError {0}): {1}").format(e.args,
                        decode_utf8(e.message)))
                return None
            else:
                log.error(_(u"SelectError ({0}): {1}").format(e.args,
                                        decode_utf8(e.message)))
                raise
        except SerialException as e:
            log.error(_(u"Can't read from printer (disconnected?) (SerialException): {0}").format(decode_utf8(str(e))))
            return None
        except socket.error as e:
            log.error(_(u"Can't read from printer (disconnected?) (Socket error {0}): {1}").format(e.errno, decode_utf8(e.strerror)))
            return None
        except OSError as e:
            if e.errno == errno.EAGAIN:  # Not a real error, no data was available
                return ""
            log.error(_(u"Can't read from printer (disconnected?) (OS Error {0}): {1}").format(e.errno, e.strerror))
            return None


class Sender(QtCore.QObject):
    send_command = QtCore.Signal(dict)
    finished = QtCore.Signal()

    def __init__(self, parent):
        super(Sender, self).__init__()
        self.parent = parent

    def sender(self):
        print "inside sender method (running sender thread)"
        while not self.parent.stop_send_thread:
            try:
                command = self.parent.priqueue.get(True, 0.1)
            except QueueEmpty:
                continue
            while self.parent.printer and self.parent.printing and not \
                    self.parent.clear:
                time.sleep(0.001)
            self.parent._send(command)
            while self.parent.printer and self.parent.printing and not \
                    self.parent.clear:
                time.sleep(0.001)

        print "finishing inside sender method"
        self.finished.emit()


class Printer(QtCore.QObject):
    pause_sig = QtCore.Signal()
    finished = QtCore.Signal()

    def __init__(self, parent, resuming=False):
        super(Printer, self).__init__()
        self.parent = parent
        self.resuming = resuming

    def _print(self):
        self.parent._stop_sender()
        try:
            if self.parent.startcb:
                try: 
                    self.parent.startcb(self.resuming)
                except:
                    log.error(_("Print start callback failed with: {}".format(traceback.format_exc())))
                    self.parent.parent.setStatusbar(_("Printing failed to start"))
            while self.parent.printing and self.parent.printer and self.parent.online:
                self._sendnext()
            self.parent.sentlines = {}
            self.parent.log.clear()
            self.parent.sent = []
            if self.parent.endcb:
                try:
                    self.parent.endcb()
                except:
                    log.error(_("Print end callback failed with: {}".format(traceback.format_exc())))
        except Exception as e:
            log.error(
                _("Print thread died due to the following error: {0}; {1}".format(e, traceback.format_exc()))
                )
            self.parent.parent.setStatusbar(_("Printing aborted due to errors. See error log for details."))
        finally:
            self.finished.emit()

    def _sendnext(self):
        if not self.parent.printer:
            log.debug("No printer; exiting")
            return
        while self.parent.printer and self.parent.printing and not self.parent.clear:
            time.sleep(0.001)
        # Only wait for oks when using serial connections or when not using tcp
        # in streaming mode
        if not self.parent.printer_tcp or not self.parent.tcp_streaming_mode:
            self.parent.clear = False
        if not (self.parent.printing and self.parent.printer and self.parent.online):
            self.parent.clear = True
            return
        if self.parent.resendfrom < self.parent.lineno and self.parent.resendfrom > -1:
            self.parent._send(self.parent.sentlines[self.parent.resendfrom], self.parent.resendfrom, False)
            self.parent.resendfrom += 1
            return
        self.parent.resendfrom = -1
        if not self.parent.priqueue.empty():
            self.parent._send(self.parent.priqueue.get_nowait())
            self.parent.priqueue.task_done()
            return
        if self.parent.printing and self.parent.queueindex < len(self.parent.mainqueue):
            (layer, line) = self.parent.mainqueue.idxs(self.parent.queueindex)
            gline = self.parent.mainqueue.all_layers[layer][line]
            if self.parent.layerchangecb and self.parent.queueindex > 0:
                (prev_layer, prev_line) = self.parent.mainqueue.idxs(self.parent.queueindex - 1)
                if prev_layer != layer:
                    try:
                        self.parent.layerchangecb(layer)
                    except:
                        log.error(traceback.format_exc())
                        self.parent.parent.setStatusbar(_("Error occured during printing"))
            if self.parent.preprintsendcb:
                if self.parent.queueindex + 1 < len(self.parent.mainqueue):
                    (next_layer, next_line) = self.parent.mainqueue.idxs(self.parent.queueindex + 1)
                    next_gline = self.parent.mainqueue.all_layers[next_layer][next_line]
                else:
                    next_gline = None
                gline = self.parent.preprintsendcb(gline, next_gline)
            if gline is None:
                self.parent.queueindex += 1
                self.parent.clear = True
                return
            tline = gline.raw
            if tline.lstrip().startswith(";@"):  # check for host command
                self.process_host_command(tline)
                self.parent.queueindex += 1
                self.parent.clear = True
                return

            # Strip comments
            tline = gcoder.gcode_strip_comment_exp.sub("", tline).strip()
            if tline:
                self.parent._send(tline, self.parent.lineno, True)
                self.parent.lineno += 1
                if self.parent.printsendcb:
                    try: self.parent.printsendcb(gline)
                    except: log.error(traceback.print_exc())
            else:
                self.parent.clear = True
            self.parent.queueindex += 1
        else:
            self.parent.printing = False
            self.parent.clear = True
            if not self.parent.paused:
                self.parent.queueindex = 0
                self.parent.lineno = 0
                self.parent._send("M110", -1, True)

    def process_host_command(self, command):
        """only ;@pause command is implemented as a host command in printcore, but hosts are free to reimplement this method"""
        command = command.lstrip()
        if command.startswith(";@pause"):
            # self.parent.pause()
            self.pause_sig.emit()
