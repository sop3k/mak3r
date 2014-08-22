"""
Slice engine communication.
This module handles all communication with the slicing engine.
"""
__copyright__ = "Copyright (C) 2013 David Braam - Released under terms of the AGPLv3 License"
import subprocess
import time
import math
import numpy
import os
import warnings
import traceback
import platform
import sys
import urllib
import urllib2
import hashlib
import socket
import struct
import errno
import cStringIO as StringIO

from PySide import QtCore

from omni3dapp.util import profile
from omni3dapp.util import pluginInfo
from omni3dapp.util import version
from omni3dapp.util import gcodeInterpreter
from omni3dapp.logger import log


def getEngineFilename():
    """
        Finds and returns the path to the current engine executable. This is OS depended.
    :return: The full path to the engine executable.
    """
    if platform.system() == 'Windows':
        if version.isDevVersion() and os.path.exists('C:/Software/Cura_SteamEngine/_bin/Release/Cura_SteamEngine.exe'):
            return 'C:/Software/Cura_SteamEngine/_bin/Release/Cura_SteamEngine.exe'
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'CuraEngine.exe'))
    if hasattr(sys, 'frozen'):
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../..', 'CuraEngine'))
    if os.path.isfile('/usr/bin/CuraEngine'):
        return '/usr/bin/CuraEngine'
    if os.path.isfile('/usr/local/bin/CuraEngine'):
        return '/usr/local/bin/CuraEngine'
    tempPath = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..', 'CuraEngine'))
    if os.path.isdir(tempPath):
        tempPath = os.path.join(tempPath,'CuraEngine')
    return tempPath

class EngineResult(object):
    """
    Result from running the CuraEngine.
    Contains the engine log, polygons retrieved from the engine, the GCode and some meta-data.
    """
    def __init__(self):
        self._engineLog = []
        self._gcodeData = StringIO.StringIO()
        self._polygons = []
        self._replaceInfo = {}
        self._printTimeSeconds = None
        self._filamentMM = [0.0] * 4
        self._modelHash = None
        self._profileString = profile.getProfileString()
        self._preferencesString = profile.getPreferencesString()
        self._gcodeInterpreter = gcodeInterpreter.gcode()
        self._gcodeLoadThread = None
        self._finished = False

    def getFilamentWeight(self, e=0):
        #Calculates the weight of the filament in kg
        radius = float(profile.getProfileSetting('filament_diameter')) / 2
        volumeM3 = (self._filamentMM[e] * (math.pi * radius * radius)) / (1000*1000*1000)
        return volumeM3 * profile.getPreferenceFloat('filament_physical_density')

    def getFilamentCost(self, e=0):
        cost_kg = profile.getPreferenceFloat('filament_cost_kg')
        cost_meter = profile.getPreferenceFloat('filament_cost_meter')
        if cost_kg > 0.0 and cost_meter > 0.0:
            return "%.2f / %.2f" % (self.getFilamentWeight(e) * cost_kg, self._filamentMM[e] / 1000.0 * cost_meter)
        elif cost_kg > 0.0:
            return "%.2f" % (self.getFilamentWeight(e) * cost_kg)
        elif cost_meter > 0.0:
            return "%.2f" % (self._filamentMM[e] / 1000.0 * cost_meter)
        return None

    def getPrintTime(self):
        if self._printTimeSeconds is None:
            return ''
        if int(self._printTimeSeconds / 60 / 60) < 1:
            return '%d minutes' % (int(self._printTimeSeconds / 60) % 60)
        if int(self._printTimeSeconds / 60 / 60) == 1:
            return '%d hour %d minutes' % (int(self._printTimeSeconds / 60 / 60), int(self._printTimeSeconds / 60) % 60)
        return '%d hours %d minutes' % (int(self._printTimeSeconds / 60 / 60), int(self._printTimeSeconds / 60) % 60)

    def getFilamentAmount(self, e=0):
        if self._filamentMM[e] == 0.0:
            return None
        return '%0.2f meter %0.0f gram' % (float(self._filamentMM[e]) / 1000.0, self.getFilamentWeight(e) * 1000.0)

    def getLog(self):
        return self._engineLog

    def getGCode(self):
        data = self._gcodeData.getvalue()
        if len(self._replaceInfo) > 0:
            block0 = data[0:2048]
            for k, v in self._replaceInfo.items():
                v = (v + ' ' * len(k))[:len(k)]
                block0 = block0.replace(k, v)
            return block0 + data[2048:]
        return data

    def setGCode(self, gcode):
        self._gcodeData = StringIO.StringIO(gcode)
        self._replaceInfo = {}

    def addLog(self, line):
        self._engineLog.append(line)

    def setHash(self, hash):
        self._modelHash = hash

    def setFinished(self, result):
        self._finished = result

    def isFinished(self):
        return self._finished

    def _gcodeInterpreterCallback(self, progress):
        if len(self._gcodeInterpreter.layerList) % 5 == 0:
            time.sleep(0.1)
        return self._gcodeLoadCallback(self, progress)

    def getGCodeLayers(self, loadCallback):
        if not self._finished:
            return None
        if self._gcodeInterpreter.layerList is None and self._gcodeLoadThread is None:
            self._gcodeInterpreter.progressCallback = self._gcodeInterpreterCallback
            signal = GCodeInterpreterSignal()
            self._gcodeLoadThread = EngineThread(self._parent,
                    signal.gcode_interpret_sig, {'gcodeData': self._gcodeData})
            self._gcodeLoadThread.signal = signal
            self._gcodeLoadThread.signal.gcode_interpret_sig.connect(self._gcodeInterpreter.load(self._gcodeData))
            # self._gcodeLoadThread = EngineThread(parent=self._parent, func=lambda : self._gcodeInterpreter.load(self._gcodeData))
            # self._gcodeLoadThread = threading.Thread(target=lambda : self._gcodeInterpreter.load(self._gcodeData))
            self._gcodeLoadCallback = loadCallback
            # self._gcodeLoadThread.daemon = True
            self._gcodeLoadThread.start()
        return self._gcodeInterpreter.layerList

    # def submitInfoOnline(self):
    #     if profile.getPreference('submit_slice_information') != 'True':
    #         return
    #     if version.isDevVersion():
    #         return
    #     data = {
    #         'processor': platform.processor(),
    #         'machine': platform.machine(),
    #         'platform': platform.platform(),
    #         'profile': self._profileString,
    #         'preferences': self._preferencesString,
    #         'modelhash': self._modelHash,
    #         'version': version.getVersion(),
    #     }
    #     try:
    #         f = urllib2.urlopen("https://www.youmagine.com/curastats/", data = urllib.urlencode(data), timeout = 1)
    #         f.read()
    #         f.close()
    #     except:
    #         traceback.print_exc()


class GCodeInterpreterSignal(QtCore.QObject):
    gcode_interpret_sig = QtCore.Signal(dict)


class SocketListener(QtCore.QObject):
    start_socket_connector_sig = QtCore.Signal(socket._socketobject)
    finished = QtCore.Signal()

    def __init__(self, parent, server_socket, server_port_nr):
        super(SocketListener, self).__init__()
        self.parent = parent
        self.server_socket = server_socket
        self.server_port_nr = server_port_nr

    def socketListen(self):
        self.server_socket.listen(1)
        print 'Listening for engine communications on %d' % (self.server_port_nr)
        while True:
            try:
                sock, _ = self.server_socket.accept()
                self.start_socket_connector_sig.emit(sock)
            except socket.error, e:
                if e.errno != errno.EINTR:
                    raise
                else:
                    log.error(e)
        self.finished.emit()


class SocketConnector(QtCore.QObject):
    GUI_CMD_REQUEST_MESH = 0x01
    GUI_CMD_SEND_POLYGONS = 0x02
    GUI_CMD_FINISH_OBJECT = 0x03

    finished = QtCore.Signal()

    def __init__(self, engine, sock, model_data):
        super(SocketConnector, self).__init__()
        self.engine = engine
        self.sock = sock
        self.model_data = model_data

    def socketConnect(self):
        layer_nr_offset = 0
        while True:
            try:
                data = self.sock.recv(4)
            except Exception, e:
                log.error(e)
                data = ''
            if len(data) == 0:
                self.sock.close()
                self.finished.emit()
                return
            cmd = struct.unpack('@i', data)[0]
            if cmd == self.GUI_CMD_REQUEST_MESH:
                try:
                    mesh_info = self.model_data[0]
                    self.model_data = self.model_data[1:]
                    self.sock.sendall(struct.pack('@i', mesh_info[0]))
                    self.sock.sendall(mesh_info[1].tostring())
                except (socket.error, IndexError), e:
                    log.error(e)
            elif cmd == self.GUI_CMD_SEND_POLYGONS:
                cnt = struct.unpack('@i', self.sock.recv(4))[0]
                layer_nr = struct.unpack('@i', self.sock.recv(4))[0]
                layer_nr += layer_nr_offset
                z = struct.unpack('@i', self.sock.recv(4))[0]
                z = float(z) / 1000.0
                type_name_len = struct.unpack('@i', self.sock.recv(4))[0]
                type_name = self.sock.recv(type_name_len)

                if self.engine._result is not None:
                    while len(self.engine._result._polygons) < layer_nr + 1:
                        self.engine._result._polygons.append({})
                    polygons = self.engine._result._polygons[layer_nr]
                    if type_name not in polygons:
                        polygons[type_name] = []
                    for n in xrange(0, cnt):
                        length = struct.unpack('@i', self.sock.recv(4))[0]
                        data = ''
                        while len(data) < length * 8 * 2:
                            recv_data = self.sock.recv(length * 8 * 2 - len(data))
                            if len(recv_data) < 1:
                                return
                            data += recv_data
                        polygon2d = numpy.array(numpy.fromstring(data, numpy.int64), numpy.float32) / 1000.0
                        polygon2d = polygon2d.reshape((len(polygon2d) / 2, 2))
                        polygon = numpy.empty((len(polygon2d), 3), numpy.float32)
                        polygon[:,:-1] = polygon2d
                        polygon[:,2] = z
                        polygons[type_name].append(polygon)
            elif cmd == self.GUI_CMD_FINISH_OBJECT:
                layer_nr_offset = len(self.engine._result._polygons)
            else:
                log.debug("Unknown command on socket: %x" % (cmd))


class ProcessObserver(QtCore.QObject):
    set_process_sig = QtCore.Signal(list)
    stop_process_sig = QtCore.Signal()
    update_progress_sig = QtCore.Signal(float)
    start_log_thread_sig = QtCore.Signal(file)
    stop_log_thread_sig = QtCore.Signal()
    finished = QtCore.Signal()

    def __init__(self, engine, command_list, model_hash):
        super(ProcessObserver, self).__init__()
        self.engine = engine
        self.command_list = command_list
        self.model_hash = model_hash

    def run_engine_process(self, cmd_list):
        kwargs = {}
        if subprocess.mswindows:
            su = subprocess.STARTUPINFO()
            su.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            su.wShowWindow = subprocess.SW_HIDE
            kwargs['startupinfo'] = su
            kwargs['creationflags'] = 0x00004000 #BELOW_NORMAL_PRIORITY_CLASS
        return subprocess.Popen(cmd_list, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)

    def watchProcess(self):
        self.stop_process_sig.emit()
        self.update_progress_sig.emit(-1.0)
        try:
            self.process = self.run_engine_process(self.command_list)
            self.set_process_sig.emit([self.process,])
        except OSError, e:
            log.error(e)
            traceback.print_exc()
            self.finished.emit()
            return
        # if self._thread != QtCore.QThread.currentThread() and self._process:
        #     self._process.terminate()

        self.engine._result = EngineResult()
        self.engine._result.addLog('Running: %s' % (''.join(self.command_list)))
        self.engine._result.setHash(self.model_hash)
        self.update_progress_sig.emit(0.0)

        self.start_log_thread_sig.emit(self.process.stderr)

        data = self.process.stdout.read(4096)
        while len(data) > 0:
            self.engine._result._gcodeData.write(data)
            data = self.process.stdout.read(4096)

        returnCode = self.process.wait()
        # self.stop_log_thread_sig.emit()
        if returnCode == 0:
            pluginError = pluginInfo.runPostProcessingPlugins(self.engine._result)
            if pluginError is not None:
                print pluginError
                self.engine._result.addLog(pluginError)
            # self.engine._result.setFinished(True)
            # self.update_progress_sig.emit(1.0)
        else:
            for line in self.engine._result.getLog():
                print line
            self.update_progress_sig.emit(-1.0)
        self.process = None
        self.set_process_sig.emit([self.process,])
        self.finished.emit()


class StdErrObserver(QtCore.QObject):
    _progress_steps = ['inset', 'skin', 'export']
    update_progress_sig = QtCore.Signal(float)
    finished = QtCore.Signal()
    
    def __init__(self, engine, stderr):
        super(StdErrObserver, self).__init__()
        self.engine = engine
        self.stderr = stderr

    def watchStdErr(self):
        object_nr = 0
        obj_count = self.engine.getObjCount()
        line = self.stderr.readline()
        while len(line) > 0:
            line = line.strip()
            if line.startswith('Progress:'):
                line = line.split(':')
                if line[1] == 'process':
                    object_nr += 1
                elif line[1] in self._progress_steps:
                    try:
                        progress_value = float(line[2]) / float(line[3])
                        progress_value /= len(self._progress_steps)
                        progress_value += 1.0 / len(self._progress_steps) * self._progress_steps.index(line[1])

                        progress_value /= obj_count
                        progress_value += 1.0 / obj_count * object_nr

                        self.update_progress_sig.emit(progress_value)
                        # TODO: fix the workoround below
                        time.sleep(0.01)
                    except Exception, e:
                        log.error(e)
            elif line.startswith('Print time:'):
                self.engine._result._printTimeSeconds = int(line.split(':')[1].strip())
            elif line.startswith('Filament:'):
                self.engine._result._filamentMM[0] = int(line.split(':')[1].strip())
                if profile.getMachineSetting('gcode_flavor') == 'UltiGCode':
                    radius = profile.getProfileSettingFloat('filament_diameter') / 2.0
                    self.engine._result._filamentMM[0] /= (math.pi * radius * radius)
            elif line.startswith('Filament2:'):
                self.engine._result._filamentMM[1] = int(line.split(':')[1].strip())
                if profile.getMachineSetting('gcode_flavor') == 'UltiGCode':
                    radius = profile.getProfileSettingFloat('filament_diameter') / 2.0
                    self.engine._result._filamentMM[1] /= (math.pi * radius * radius)
            elif line.startswith('Replace:'):
                self.engine._result._replaceInfo[line.split(':')[1].strip()] = line.split(':')[2].strip()
            else:
                self.engine._result.addLog(line)
            line = self.stderr.readline()
        self.engine._result.setFinished(True)
        self.update_progress_sig.emit(1.0)
        self.finished.emit()


class Engine(QtCore.QObject):
    """
    Class used to communicate with the CuraEngine.
    The CuraEngine is ran as a 2nd process and reports back information trough stderr.
    GCode through stdout and has a socket connection for polygon information and loading the 3D model into the engine.
    """

    def __init__(self, sceneview, progressCallback):
        super(Engine, self).__init__(sceneview)
        self._sceneview = sceneview
        self._parent = sceneview._parent
        self._process = None
        self._thread = None
        self._callback = progressCallback
        self._objCount = 0
        self._result = None
        self._modelData = None
        self.runner = None

        self._serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._serverPortNr = 0xC20A

        self.bind_server_socket()

        self.socket_listener = SocketListener(self._parent, self._serversocket,
                self._serverPortNr)
        thread = QtCore.QThread(self._parent)
        self.socket_listener.moveToThread(thread)

        thread.started.connect(self.socket_listener.socketListen) 
        self.socket_listener.finished.connect(thread.quit)
        self.socket_listener.finished.connect(self.socket_listener.deleteLater)
        self.socket_listener.start_socket_connector_sig.connect(self.startSocketConnector)
        thread.finished.connect(thread.deleteLater)

        thread.start()

    def bind_server_socket(self):
        while True:
            try:
                self._serversocket.bind(('127.0.0.1', self._serverPortNr))
            except socket.error:
                log.error("Failed to listen on port: %d" % (self._serverPortNr))
                self._serverPortNr += 1
                if self._serverPortNr > 0xFFFF:
                    log.error("Failed to listen on any port...")
                    return
            else:
                return

    def startSocketConnector(self, sock):
        self.socket_connector = SocketConnector(self, sock, self._modelData)
        thread = QtCore.QThread(self._parent)
        self.socket_connector.moveToThread(thread)

        thread.started.connect(self.socket_connector.socketConnect)
        self.socket_connector.finished.connect(thread.quit)
        self.socket_connector.finished.connect(self.socket_connector.deleteLater)
        thread.finished.connect(thread.deleteLater)

        thread.start()

    def startLogThread(self, stderr):
        self.log_thread = QtCore.QThread(self._parent)
        self.stderr_observer = StdErrObserver(self, stderr)
        self.stderr_observer.moveToThread(self.log_thread)

        self.log_thread.started.connect(self.stderr_observer.watchStdErr)
        self.stderr_observer.update_progress_sig.connect(self._callback,
                QtCore.Qt.QueuedConnection)
        self.stderr_observer.finished.connect(self.log_thread.quit)
        self.stderr_observer.finished.connect(self.stderr_observer.deleteLater)
        self.log_thread.finished.connect(self.log_thread.deleteLater)

        self.log_thread.start()

    def stopLogThread(self):
        if getattr(self, 'log_thread', None):
            try:
                self.log_thread.terminate()
            except RuntimeError, e:
                log.error(e)
        self.log_thread = None

    @QtCore.Slot(list)
    def setProcess(self, attrs):
        self._process = attrs[0]

    def stopProcess(self):
        if self._process is not None:
            self._process.terminate()

    def setModelData(self, model_data):
        self._modelData = model_data

    def getObjCount(self):
        return self._objCount

    def setObjCount(self, obj_count):
        self._objCount = obj_count

    def cleanup(self):
        self.abortEngine()
        self._serversocket.close()

    def abortEngine(self):
        if self._process is not None:
            try:
                self._process.terminate()
            except Exception, e:
                log.error(e)
        if self.runner and self.runner._thread:
            self.runner._thread.terminate()
            self.runner._thread = None

    def wait(self):
        if self.runner and self.runner._thread:
            self.runner._thread.terminate()

    def getResult(self):
        return self._result

    def getServerPortNr(self):
        return self._serverPortNr

    def runEngine(self, scene):
        if len(scene.objects()) < 1:
            return
        self.runner = EngineRunner(scene, self)

    def _engineSettings(self, extruderCount):
        settings = {
            'layerThickness': int(profile.getProfileSettingFloat('layer_height') * 1000),
            'initialLayerThickness': int(profile.getProfileSettingFloat('bottom_thickness') * 1000) if profile.getProfileSettingFloat('bottom_thickness') > 0.0 else int(profile.getProfileSettingFloat('layer_height') * 1000),
            'filamentDiameter': int(profile.getProfileSettingFloat('filament_diameter') * 1000),
            'filamentFlow': int(profile.getProfileSettingFloat('filament_flow')),
            'extrusionWidth': int(profile.calculateEdgeWidth() * 1000),
            'layer0extrusionWidth': int(profile.calculateEdgeWidth() * profile.getProfileSettingFloat('layer0_width_factor') / 100 * 1000),
            'insetCount': int(profile.calculateLineCount()),
            'downSkinCount': int(profile.calculateSolidLayerCount()) if profile.getProfileSetting('solid_bottom') == 'True' else 0,
            'upSkinCount': int(profile.calculateSolidLayerCount()) if profile.getProfileSetting('solid_top') == 'True' else 0,
            'infillOverlap': int(profile.getProfileSettingFloat('fill_overlap')),
            'initialSpeedupLayers': int(4),
            'initialLayerSpeed': int(profile.getProfileSettingFloat('bottom_layer_speed')),
            'printSpeed': int(profile.getProfileSettingFloat('print_speed')),
            'infillSpeed': int(profile.getProfileSettingFloat('infill_speed')) if int(profile.getProfileSettingFloat('infill_speed')) > 0 else int(profile.getProfileSettingFloat('print_speed')),
            'inset0Speed': int(profile.getProfileSettingFloat('inset0_speed')) if int(profile.getProfileSettingFloat('inset0_speed')) > 0 else int(profile.getProfileSettingFloat('print_speed')),
            'insetXSpeed': int(profile.getProfileSettingFloat('insetx_speed')) if int(profile.getProfileSettingFloat('insetx_speed')) > 0 else int(profile.getProfileSettingFloat('print_speed')),
            'moveSpeed': int(profile.getProfileSettingFloat('travel_speed')),
            'fanSpeedMin': int(profile.getProfileSettingFloat('fan_speed')) if profile.getProfileSetting('fan_enabled') == 'True' else 0,
            'fanSpeedMax': int(profile.getProfileSettingFloat('fan_speed_max')) if profile.getProfileSetting('fan_enabled') == 'True' else 0,
            'supportAngle': int(-1) if profile.getProfileSetting('support') == 'None' else int(profile.getProfileSettingFloat('support_angle')),
            'supportEverywhere': int(1) if profile.getProfileSetting('support') == 'Everywhere' else int(0),
            'supportLineDistance': int(100 * profile.calculateEdgeWidth() * 1000 / profile.getProfileSettingFloat('support_fill_rate')) if profile.getProfileSettingFloat('support_fill_rate') > 0 else -1,
            'supportXYDistance': int(1000 * profile.getProfileSettingFloat('support_xy_distance')),
            'supportZDistance': int(1000 * profile.getProfileSettingFloat('support_z_distance')),
            'supportExtruder': 0 if profile.getProfileSetting('support_dual_extrusion') == 'First extruder' else (1 if profile.getProfileSetting('support_dual_extrusion') == 'Second extruder' and profile.minimalExtruderCount() > 1 else -1),
            'retractionAmount': int(profile.getProfileSettingFloat('retraction_amount') * 1000) if profile.getProfileSetting('retraction_enable') == 'True' else 0,
            'retractionSpeed': int(profile.getProfileSettingFloat('retraction_speed')),
            'retractionMinimalDistance': int(profile.getProfileSettingFloat('retraction_min_travel') * 1000),
            'retractionAmountExtruderSwitch': int(profile.getProfileSettingFloat('retraction_dual_amount') * 1000),
            'retractionZHop': int(profile.getProfileSettingFloat('retraction_hop') * 1000),
            'minimalExtrusionBeforeRetraction': int(profile.getProfileSettingFloat('retraction_minimal_extrusion') * 1000),
            'enableCombing': 1 if profile.getProfileSetting('retraction_combing') == 'True' else 0,
            'multiVolumeOverlap': int(profile.getProfileSettingFloat('overlap_dual') * 1000),
            'objectSink': max(0, int(profile.getProfileSettingFloat('object_sink') * 1000)),
            'minimalLayerTime': int(profile.getProfileSettingFloat('cool_min_layer_time')),
            'minimalFeedrate': int(profile.getProfileSettingFloat('cool_min_feedrate')),
            'coolHeadLift': 1 if profile.getProfileSetting('cool_head_lift') == 'True' else 0,
            'startCode': profile.getAlterationFileContents('startgcode', extruderCount),
            'endCode': profile.getAlterationFileContents('endgcode', extruderCount),
            'preSwitchExtruderCode': profile.getAlterationFileContents('preSwitchExtruder.gcode', extruderCount),
            'postSwitchExtruderCode': profile.getAlterationFileContents('postSwitchExtruder.gcode', extruderCount),

            'extruderOffset[1].X': int(profile.getMachineSettingFloat('extruder_offset_x1') * 1000),
            'extruderOffset[1].Y': int(profile.getMachineSettingFloat('extruder_offset_y1') * 1000),
            'extruderOffset[2].X': int(profile.getMachineSettingFloat('extruder_offset_x2') * 1000),
            'extruderOffset[2].Y': int(profile.getMachineSettingFloat('extruder_offset_y2') * 1000),
            'extruderOffset[3].X': int(profile.getMachineSettingFloat('extruder_offset_x3') * 1000),
            'extruderOffset[3].Y': int(profile.getMachineSettingFloat('extruder_offset_y3') * 1000),
            'fixHorrible': 0,
        }
        fanFullHeight = int(profile.getProfileSettingFloat('fan_full_height') * 1000)
        settings['fanFullOnLayerNr'] = (fanFullHeight - settings['initialLayerThickness'] - 1) / settings['layerThickness'] + 1
        if settings['fanFullOnLayerNr'] < 0:
            settings['fanFullOnLayerNr'] = 0
        if profile.getProfileSetting('support_type') == 'Lines':
            settings['supportType'] = 1

        if profile.getProfileSettingFloat('fill_density') == 0:
            settings['sparseInfillLineDistance'] = -1
        elif profile.getProfileSettingFloat('fill_density') == 100:
            settings['sparseInfillLineDistance'] = settings['extrusionWidth']
            #Set the up/down skins height to 10000 if we want a 100% filled object.
            # This gives better results then normal 100% infill as the sparse and up/down skin have some overlap.
            settings['downSkinCount'] = 10000
            settings['upSkinCount'] = 10000
        else:
            settings['sparseInfillLineDistance'] = int(100 * profile.calculateEdgeWidth() * 1000 / profile.getProfileSettingFloat('fill_density'))
        if profile.getProfileSetting('platform_adhesion') == 'Brim':
            settings['skirtDistance'] = 0
            settings['skirtLineCount'] = int(profile.getProfileSettingFloat('brim_line_count'))
        elif profile.getProfileSetting('platform_adhesion') == 'Raft':
            settings['skirtDistance'] = 0
            settings['skirtLineCount'] = 0
            settings['raftMargin'] = int(profile.getProfileSettingFloat('raft_margin') * 1000)
            settings['raftLineSpacing'] = int(profile.getProfileSettingFloat('raft_line_spacing') * 1000)
            settings['raftBaseThickness'] = int(profile.getProfileSettingFloat('raft_base_thickness') * 1000)
            settings['raftBaseLinewidth'] = int(profile.getProfileSettingFloat('raft_base_linewidth') * 1000)
            settings['raftInterfaceThickness'] = int(profile.getProfileSettingFloat('raft_interface_thickness') * 1000)
            settings['raftInterfaceLinewidth'] = int(profile.getProfileSettingFloat('raft_interface_linewidth') * 1000)
            settings['raftInterfaceLineSpacing'] = int(profile.getProfileSettingFloat('raft_interface_linewidth') * 1000 * 2.0)
            settings['raftAirGapLayer0'] = int(profile.getProfileSettingFloat('raft_airgap') * 1000)
            settings['raftBaseSpeed'] = int(profile.getProfileSettingFloat('bottom_layer_speed'))
            settings['raftFanSpeed'] = 100
            settings['raftSurfaceThickness'] = settings['raftInterfaceThickness']
            settings['raftSurfaceLinewidth'] = int(profile.calculateEdgeWidth() * 1000)
            settings['raftSurfaceLineSpacing'] = int(profile.calculateEdgeWidth() * 1000 * 0.9)
            settings['raftSurfaceLayers'] = int(profile.getProfileSettingFloat('raft_surface_layers'))
            settings['raftSurfaceSpeed'] = int(profile.getProfileSettingFloat('bottom_layer_speed'))
        else:
            settings['skirtDistance'] = int(profile.getProfileSettingFloat('skirt_gap') * 1000)
            settings['skirtLineCount'] = int(profile.getProfileSettingFloat('skirt_line_count'))
            settings['skirtMinLength'] = int(profile.getProfileSettingFloat('skirt_minimal_length') * 1000)

        if profile.getProfileSetting('fix_horrible_union_all_type_a') == 'True':
            settings['fixHorrible'] |= 0x01
        if profile.getProfileSetting('fix_horrible_union_all_type_b') == 'True':
            settings['fixHorrible'] |= 0x02
        if profile.getProfileSetting('fix_horrible_use_open_bits') == 'True':
            settings['fixHorrible'] |= 0x10
        if profile.getProfileSetting('fix_horrible_extensive_stitching') == 'True':
            settings['fixHorrible'] |= 0x04

        if settings['layerThickness'] <= 0:
            settings['layerThickness'] = 1000
        if profile.getMachineSetting('gcode_flavor') == 'UltiGCode':
            settings['gcodeFlavor'] = 1
        elif profile.getMachineSetting('gcode_flavor') == 'MakerBot':
            settings['gcodeFlavor'] = 2
        elif profile.getMachineSetting('gcode_flavor') == 'BFB':
            settings['gcodeFlavor'] = 3
        elif profile.getMachineSetting('gcode_flavor') == 'Mach3':
            settings['gcodeFlavor'] = 4
        elif profile.getMachineSetting('gcode_flavor') == 'RepRap (Volumetric)':
            settings['gcodeFlavor'] = 5
        if profile.getProfileSetting('spiralize') == 'True':
            settings['spiralizeMode'] = 1
        if profile.getProfileSetting('simple_mode') == 'True':
            settings['simpleMode'] = 1
        if profile.getProfileSetting('wipe_tower') == 'True' and extruderCount > 1:
            settings['wipeTowerSize'] = int(math.sqrt(profile.getProfileSettingFloat('wipe_tower_volume') * 1000 * 1000 * 1000 / settings['layerThickness']))
        if profile.getProfileSetting('ooze_shield') == 'True':
            settings['enableOozeShield'] = 1
        return settings


class EngineRunner(object):
    def __init__(self, scene, engine):
        self.scene = scene
        self.engine = engine
        self.obj_count = 0
        self.command_list = []
        self.model_hash = None
        self._thread = None

        self.setup()

        if self.obj_count > 0:
            self._thread = QtCore.QThread(engine._sceneview)
            self.process_observer = ProcessObserver(self.engine, self.command_list, self.model_hash)
            self.process_observer.moveToThread(self._thread)

            self._thread.started.connect(self.process_observer.watchProcess)
            self.process_observer.stop_process_sig.connect(engine.stopProcess)
            self.process_observer.set_process_sig.connect(engine.setProcess)
            self.process_observer.update_progress_sig.connect(engine._callback)
            self.process_observer.start_log_thread_sig.connect(engine.startLogThread)
            self.process_observer.stop_log_thread_sig.connect(engine.stopLogThread,
                    QtCore.Qt.DirectConnection)
            self.process_observer.finished.connect(self._thread.quit)
            self.process_observer.finished.connect(self.process_observer.deleteLater)
            self.process_observer.finished.connect(self.delete_thread)
            self._thread.finished.connect(self._thread.deleteLater)

            self._thread.start()

    def delete_thread(self):
        self._thread = None

    def get_extruder_count(self):
        extruderCount = 1
        for obj in self.scene.objects():
            if self.scene.checkPlatform(obj):
                extruderCount = max(extruderCount, len(obj._meshList))

        return max(extruderCount, profile.minimalExtruderCount())

    def setup(self):
        extruder_count = self.get_extruder_count()
        self.command_list = [getEngineFilename(), '-v', '-p']
        for k, v in self.engine._engineSettings(extruder_count).iteritems():
            self.command_list += ['-s', '%s=%s' % (k, str(v))]
        self.command_list += ['-g', '%d' % (self.engine.getServerPortNr())]

        objCount = 0
        engineModelData = []
        hash = hashlib.sha512()
        order = self.scene.printOrder()
        if order is None:
            pos = numpy.array(profile.getMachineCenterCoords()) * 1000
            objMin = None
            objMax = None
            for obj in self.scene.objects():
                if self.scene.checkPlatform(obj):
                    oMin = obj.getMinimum()[0:2] + obj.getPosition()
                    oMax = obj.getMaximum()[0:2] + obj.getPosition()
                    if objMin is None:
                        objMin = oMin
                        objMax = oMax
                    else:
                        objMin[0] = min(oMin[0], objMin[0])
                        objMin[1] = min(oMin[1], objMin[1])
                        objMax[0] = max(oMax[0], objMax[0])
                        objMax[1] = max(oMax[1], objMax[1])
            if objMin is None:
                return
            pos += (objMin + objMax) / 2.0 * 1000
            self.command_list += ['-s', 'posx=%d' % int(pos[0]), '-s', 'posy=%d' % int(pos[1])]

            vertexTotal = [0] * 4
            meshMax = 1
            for obj in self.scene.objects():
                if self.scene.checkPlatform(obj):
                    meshMax = max(meshMax, len(obj._meshList))
                    for n in xrange(0, len(obj._meshList)):
                        vertexTotal[n] += obj._meshList[n].vertexCount

            for n in xrange(0, meshMax):
                verts = numpy.zeros((0, 3), numpy.float32)
                for obj in self.scene.objects():
                    if self.scene.checkPlatform(obj):
                        if n < len(obj._meshList):
                            vertexes = (numpy.matrix(obj._meshList[n].vertexes, copy = False) * numpy.matrix(obj._matrix, numpy.float32)).getA()
                            vertexes -= obj._drawOffset
                            vertexes += numpy.array([obj.getPosition()[0], obj.getPosition()[1], 0.0])
                            verts = numpy.concatenate((verts, vertexes))
                            hash.update(obj._meshList[n].vertexes.tostring())
                engineModelData.append((vertexTotal[n], verts))

            self.command_list += ['$' * meshMax]
            objCount = 1
        else:
            for n in order:
                obj = self.scene.objects()[n]
                for mesh in obj._meshList:
                    engineModelData.append((mesh.vertexCount, mesh.vertexes))
                    hash.update(mesh.vertexes.tostring())
                pos = obj.getPosition() * 1000
                pos += numpy.array(profile.getMachineCenterCoords()) * 1000
                self.command_list += ['-m', ','.join(map(str, obj._matrix.getA().flatten()))]
                self.command_list += ['-s', 'posx=%d' % int(pos[0]), '-s', 'posy=%d' % int(pos[1])]
                self.command_list += ['$' * len(obj._meshList)]
                objCount += 1
        self.model_hash = hash.hexdigest()
        self.engine.setObjCount(objCount)
        self.obj_count = objCount
        if objCount > 0:
            self.engine.setModelData(engineModelData)
