import os
import glob
import threading
if os.name == "nt":
    try:
        import _winreg
    except:
        pass

from serial import SerialException

from omni3dapp.util import profile
from omni3dapp.util.printing.pronsole import Pronsole
from omni3dapp.util.printing.printcore import Printcore
from omni3dapp.logger import log


class PrinterConnection(Pronsole):
    """
    Handles connecting to printer and storing a state of printing
    """
    def __init__(self, ui):
        Pronsole.__init__(self)
        self.ui = ui
        self.paused = False
        self.sdprinting = False
        self.predisconnect_mainqueue = None

    def scanserial(self):
        """scan for available ports. return a list of device names."""
        baselist = []
        if os.name == "nt":
            try:
                key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE, "HARDWARE\\DEVICEMAP\\SERIALCOMM")
                i = 0
                while(1):
                    baselist += [_winreg.EnumValue(key, i)[1]]
                    i += 1
            except:
                log.error("Failed to open key from winreg")
    
        for g in ['/dev/ttyUSB*', '/dev/ttyACM*', "/dev/tty.*", "/dev/cu.*", "/dev/rfcomm*"]:
            baselist += glob.glob(g)
        return filter(self.bluetoothSerialFilter, baselist)
    
    def bluetoothSerialFilter(self, serial):
        return not ("Bluetooth" in serial or "FireFly" in serial)

    def connect(self, port_val, baud_val):
        if not port_val:
            scanned = self.scanserial()
            if scanned:
                port_val = scanned[0]
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
        settings_port = profile.settingsDictionary.get('port_type') or ""
        if port_val != settings_port:
            profile.settingsDictionary['port_type'].setValue(port_val)
        settings_baud = profile.settingsDictionary.get('port_baud_rate') or ""
        if baud_val != settings_baud:
            profile.settingsDictionary['port_baud_rate'].setValue(baud_val)
        if self.predisconnect_mainqueue:
            # self.recoverbtn.Enable()
            pass

    def connect_to_printer(self, port, baud):
        try:
            self.p.connect(port, baud)
        except SerialException as e:
            # Currently, there is no errno, but it should be there in the future
            if e.errno == 2:
                self.log.error(_("Error: You are trying to connect to a non-existing port."))
            elif e.errno == 8:
                self.log.error(_("Error: You don't have permission to open %s.") % port)
                self.log.error(_("You might need to add yourself to the dialout group."))
            else:
                self.log.error(traceback.format_exc())
            # Kill the scope anyway
            return False
        except OSError as e:
            if e.errno == 2:
                self.log.error(_("Error: You are trying to connect to a non-existing port."))
            else:
                self.log.error(traceback.format_exc())
            return False
        self.statuscheck = True
        self.status_thread = threading.Thread(target = self.statuschecker)
        self.status_thread.start()
        return True

    def statuschecker(self):
        Pronsole.statuschecker(self)
        # wx.CallAfter(self.statusbar.SetStatusText, _("Not connected to printer."))
        log.info(_("Not connected to printer"))

    def rescanports(self):
        scanned = self.scanserial()
        portslist = list(scanned)
        port = profile.settingsDictionary.get('port_type') or ""
        if port:
            port = port.getValue()
        if port != "" and port not in portslist:
            portslist.append(port)
        if portslist:    
            self.ui.port_type.clear()
            self.ui.port_type.addItems(portslist)
        if os.path.exists(port) or port in scanned:
            self.ui.port_type.setCurrentIndex(self.ui.port_type.findText(port))
        elif portslist:
            self.ui.port_type.setCurrentIndex(self.ui.port_type.findText(portslist[0]))
