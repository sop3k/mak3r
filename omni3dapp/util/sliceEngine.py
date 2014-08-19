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
        self._success = False
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

    def _gcodeInterpreterCallback(self, progress):
        if len(self._gcodeInterpreter.layerList) % 5 == 0:
            time.sleep(0.1)
        return self._gcodeLoadCallback(self, progress)

    def submitInfoOnline(self):
        if profile.getPreference('submit_slice_information') != 'True':
            return
        if version.isDevVersion():
            return
        data = {
            'processor': platform.processor(),
            'machine': platform.machine(),
            'platform': platform.platform(),
            'profile': self._profileString,
            'preferences': self._preferencesString,
            'modelhash': self._modelHash,
            'version': version.getVersion(),
        }
        try:
            f = urllib2.urlopen("https://www.youmagine.com/curastats/", data = urllib.urlencode(data), timeout = 1)
            f.read()
            f.close()
        except:
            traceback.print_exc()


class GCodeInterpreterSignal(QtCore.QObject):
    gcode_interpret_sig = QtCore.Signal(dict)


class SocketListener(QtCore.QObject):
    def __init__(self, parent, server_socket, server_port_nr):
        super(SocketListener, self).__init__()
        self.parent = parent
        self.server_socket = server_socket
        self.server_port_nr = server_port_nr
        self.start_socket_connector_sig = QtCore.Signal(list)

    def socketListen(self):
        print "in socket listen thread"
        self.server_socket.listen(1)
        print 'Listening for engine communications on %d' % (self.server_port_nr)
        while True:
            print "inside while loop"
            try:
                print "accepting on socket"
                sock, _ = self.server_socket.accept()
                print type(sock)
                self.start_socket_connector_sig.emit((sock))
            except socket.error, e:
                if e.errno != errno.EINTR:
                    raise
                else:
                    log.error(e)


class SocketConnector(QtCore.QObject):
    GUI_CMD_REQUEST_MESH = 0x01
    GUI_CMD_SEND_POLYGONS = 0x02
    GUI_CMD_FINISH_OBJECT = 0x03

    def __init__(self, sock, model_data, result_polygons):
        super(SocketConnector, self).__init__()
        self.sock = sock
        self.model_data = model_data
        self.result_polygons = result_polygons
        self.set_polygons_sig = QtCore.Signal(dict)

    def socketConnect(self):
        print "inside socket connect"
        layer_nr_offset = 0
        while True:
            try:
                print "receive more"
                data = self.sock.recv(4)
            except:
                data = ''
            if len(data) == 0:
                self.sock.close()
                return
            cmd = struct.unpack('@i', data)[0]
            if cmd == self.GUI_CMD_REQUEST_MESH:
                try:
                    mesh_info = self.model_data[0]
                    print "changing model data"
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
                while len(self.result_polygons) < layer_nr + 1:
                    self.result_polygons.append({})
                polygons = self.result_polygons[layer_nr]
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
                self.set_polygons_sig.emit({'polygons': polygons, 'layer_nr':
                    layer_nr})
            elif cmd == self.GUI_CMD_FINISH_OBJECT:
                layer_nr_offset = len(self.result_polygons)
            else:
                log.debug("Unknown command on socket: %x" % (cmd))


class ProcessObserver(QtCore.QObject):
    set_process_sig = QtCore.Signal(list)
    stop_process_sig = QtCore.Signal(list)
    update_progress_sig = QtCore.Signal(float)
    update_result_sig = QtCore.Signal(EngineResult)

    def __init__(self, old_thread, command_list, model_hash):
        super(ProcessObserver, self).__init__()
        self.old_thread = old_thread
        self.command_list = command_list
        self.model_hash = model_hash

    def run_engine_process(self, cmd_list):
        print "running engine process"
        kwargs = {}
        if subprocess.mswindows:
            su = subprocess.STARTUPINFO()
            su.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            su.wShowWindow = subprocess.SW_HIDE
            kwargs['startupinfo'] = su
            kwargs['creationflags'] = 0x00004000 #BELOW_NORMAL_PRIORITY_CLASS
        return subprocess.Popen(cmd_list, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)

    def watchProcess(self):
        print "inside watch process"
        # if self.old_thread is not None:
        #     self.stop_process_sig.emit([self.old_thread,])
        # self.update_progress_sig.emit(-1.0)
        # try:
        #     self.process = self.run_engine_process(self.command_list)
        #     self.set_process_sig.emit([self.process,])
        # except OSError:
        #     traceback.print_exc()
        #     return
        # # if self._thread != QtCore.QThread.currentThread() and self._process:
        # #     self._process.terminate()

        # print "setting up result"
        # self.result = EngineResult()
        # self.result.addLog('Running: %s' % (''.join(self.command_list)))
        # print "setting hash"
        # self.result.setHash(self.model_hash)
        # print "updating result"
        # self.update_result_sig.emit(self.result)
        # print "updating progress"
        # self.update_progress_sig.emit(0.0)

        # # signal = WatchStdErrSignal()
        # # logThread = EngineThread(self._parent, signal.watch_stderr_sig,
        # #         {'stderr': self._process.stderr})
        # # logThread.signal = signal
        # # logThread.signal.watch_stderr_sig.connect(self._watchStderr) 
        # # logThread.start()

        # data = self.process.stdout.read(4096)
        # while len(data) > 0:
        #     self.result._gcodeData.write(data)
        #     data = self.process.stdout.read(4096)
        # self.update_result_sig.emit(self.result)

        # returnCode = self.process.wait()
        # # logThread.wait()
        # if returnCode == 0:
        # #     pluginError = pluginInfo.runPostProcessingPlugins(self._result)
        # #     if pluginError is not None:
        # #         print pluginError
        # #         self._result.addLog(pluginError)
        #     self.result.setFinished(True)
        #     self.update_result_sig.emit(self.result)
        #     self.update_progress_sig.emit(1.0)
        # else:
        #     for line in self.result.getLog():
        #         print line
        #     self.update_progress_sig.emit(-1.0)
        # self.process = None
        # self.set_process_sig.emit([self.process,])


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
        self._progressSteps = ['inset', 'skin', 'export']
        self._objCount = 0
        self._result = None
        self._modelData = None

        self._serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._serverPortNr = 0xC20A

        self.bind_server_socket()

        worker = SocketListener(self._parent, self._serversocket,
                self._serverPortNr)
        thread = QtCore.QThread(self._parent)
        worker.moveToThread(thread)

        QtCore.QObject.connect(thread, QtCore.SIGNAL('started()'), worker,
                QtCore.SLOT('socketListen()'))
        QtCore.QObject.connect(thread,
                QtCore.SIGNAL('start_socket_connector_sig(list)'), self,
                QtCore.SLOT('startSocketConnector(list)'))
        QtCore.QObject.connect(worker, QtCore.SIGNAL('finished()'), thread,
                QtCore.SLOT('quit()'))
        QtCore.QObject.connect(worker, QtCore.SIGNAL('finished()'), worker,
                QtCore.SLOT('deleteLater()'))
        QtCore.QObject.connect(thread, QtCore.SIGNAL('finished()'), thread,
                QtCore.SLOT('deleteLater()'))
        # thread.start()

    def bind_server_socket(self):
        print "binding server socket"
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

    @QtCore.Slot(list)
    def startSocketConnector(self, attrs):
        print "in start socket connector"
        sock = attrs[0]
        if not hasattr(self._result, '_polygons'):
            return
        worker = SocketConnector(sock, self._modelData, self._result._polygons)
        thread = QtCore.QThread(self.parent)
        worker.moveToThread(thread)
        QtCore.QObject.connect(thread, QtCore.SIGNAL('started()'), worker,
                QtCore.SLOT('socketConnect()'))
        QtCore.QObject.connect(worker,
                QtCore.SIGNAL('set_polygons_sig(dict)'), self,
                QtCore.SLOT('setPolygons(dict)'))
        QtCore.QObject.connect(worker, QtCore.SIGNAL('finished()'), thread,
                QtCore.SLOT('quit()'))
        QtCore.QObject.connect(worker, QtCore.SIGNAL('finished()'), worker,
                QtCore.SLOT('deleteLater()'))
        QtCore.QObject.connect(thread, QtCore.SIGNAL('finished()'), thread,
                QtCore.SLOT('deleteLater()'))
        thread.start()

    @QtCore.Slot(dict)
    def setPolygons(self, attr_dict):
        print "setting polygons"
        polygons = attr_dict['polygons']
        layer_nr = attr_dict['layer_nr']
        self._result._polygons[layer_nr] = polygons

    @QtCore.Slot(list)
    def stopProcess(self, attrs):
        old_thread = attrs[0]
        if self._process is not None:
            self._process.terminate()
        old_thread.wait()

    @QtCore.Slot(list)
    def setProcess(self, attrs):
        self._process = attrs[0]

    @QtCore.Slot(EngineResult)
    def updateResult(self, engine_result):
        self._result = engine_result

    def setModelData(self, model_data):
        self._modelData = model_data

    def setObjCount(self, obj_count):
        self._objCount = obj_count

    def cleanup(self):
        self.abortEngine()
        self._serversocket.close()

    def abortEngine(self):
        if self._process is not None:
            try:
                self._process.terminate()
            except:
                pass
        if self._thread is not None:
            self._thread.wait()
        self._thread = None

    def wait(self):
        if self._thread is not None:
            self._thread.wait()

    def getResult(self):
        return self._result

    def getServerPortNr(self):
        return self._serverPortNr

    def runEngine(self, scene):
        print "in run engine"
        if len(scene.objects()) < 1:
            return
        extruderCount = 1
        for obj in scene.objects():
            if scene.checkPlatform(obj):
                extruderCount = max(extruderCount, len(obj._meshList))

        extruderCount = max(extruderCount, profile.minimalExtruderCount())

        commandList = [getEngineFilename(), '-v', '-p']
        for k, v in self._engineSettings(extruderCount).iteritems():
            commandList += ['-s', '%s=%s' % (k, str(v))]
        commandList += ['-g', '%d' % (self._serverPortNr)]
        self._objCount = 0
        engineModelData = []
        hash = hashlib.sha512()
        order = scene.printOrder()
        if order is None:
            pos = numpy.array(profile.getMachineCenterCoords()) * 1000
            objMin = None
            objMax = None
            for obj in scene.objects():
                if scene.checkPlatform(obj):
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
            commandList += ['-s', 'posx=%d' % int(pos[0]), '-s', 'posy=%d' % int(pos[1])]

            vertexTotal = [0] * 4
            meshMax = 1
            for obj in scene.objects():
                if scene.checkPlatform(obj):
                    meshMax = max(meshMax, len(obj._meshList))
                    for n in xrange(0, len(obj._meshList)):
                        vertexTotal[n] += obj._meshList[n].vertexCount

            for n in xrange(0, meshMax):
                verts = numpy.zeros((0, 3), numpy.float32)
                for obj in scene.objects():
                    if scene.checkPlatform(obj):
                        if n < len(obj._meshList):
                            vertexes = (numpy.matrix(obj._meshList[n].vertexes, copy = False) * numpy.matrix(obj._matrix, numpy.float32)).getA()
                            vertexes -= obj._drawOffset
                            vertexes += numpy.array([obj.getPosition()[0], obj.getPosition()[1], 0.0])
                            verts = numpy.concatenate((verts, vertexes))
                            hash.update(obj._meshList[n].vertexes.tostring())
                engineModelData.append((vertexTotal[n], verts))

            commandList += ['$' * meshMax]
            self._objCount = 1
        else:
            for n in order:
                obj = scene.objects()[n]
                for mesh in obj._meshList:
                    engineModelData.append((mesh.vertexCount, mesh.vertexes))
                    hash.update(mesh.vertexes.tostring())
                pos = obj.getPosition() * 1000
                pos += numpy.array(profile.getMachineCenterCoords()) * 1000
                commandList += ['-m', ','.join(map(str, obj._matrix.getA().flatten()))]
                commandList += ['-s', 'posx=%d' % int(pos[0]), '-s', 'posy=%d' % int(pos[1])]
                commandList += ['$' * len(obj._meshList)]
                self._objCount += 1
        modelHash = hash.hexdigest()
        if self._objCount > 0:
            self._modelData = engineModelData
            # self._thread = QtCore.QThread(self._parent)
            # worker = ProcessObserver(self._thread, commandList, modelHash)
            # worker.moveToThread(self._thread)
            # QtCore.QObject.connect(self._thread, QtCore.SIGNAL('started()'), worker,
            #         QtCore.SLOT('watchProcess()'))
            # QtCore.QObject.connect(self._thread,
            #         QtCore.SIGNAL('stop_process_sig(list)'), self,
            #         QtCore.SLOT('stopProcess(list)'))
            # QtCore.QObject.connect(self._thread,
            #         QtCore.SIGNAL('set_process_sig(list)'), self,
            #         QtCore.SLOT('setProcess(list)'))
            # QtCore.QObject.connect(self._thread,
            #         QtCore.SIGNAL('update_progress_sig(float)'), self,
            #         QtCore.SLOT('_callback(float)'))
            # QtCore.QObject.connect(self._thread,
            #         QtCore.SIGNAL('update_result_sig(EngineResult)'), self,
            #         QtCore.SLOT('updateResult(EngineResult)'))
            # QtCore.QObject.connect(worker, QtCore.SIGNAL('finished()'), self._thread,
            #         QtCore.SLOT('quit()'))
            # QtCore.QObject.connect(worker, QtCore.SIGNAL('finished()'), worker,
            #         QtCore.SLOT('deleteLater()'))
            # QtCore.QObject.connect(self._thread, QtCore.SIGNAL('finished()'),
            #         self._thread, QtCore.SLOT('deleteLater()'))
            # self._thread.start()

    def _watchStderr(self, attr_dict):
        print "in watch std err"
        stderr = attr_dict['stderr']
        objectNr = 0
        # line = stderr.readline()
        # while len(line) > 0:
        #     line = line.strip()
        #     if line.startswith('Progress:'):
        #         line = line.split(':')
        #         if line[1] == 'process':
        #             objectNr += 1
        #         elif line[1] in self._progressSteps:
        #             try:
        #                 progressValue = float(line[2]) / float(line[3])
        #                 progressValue /= len(self._progressSteps)
        #                 progressValue += 1.0 / len(self._progressSteps) * self._progressSteps.index(line[1])

        #                 progressValue /= self._objCount
        #                 progressValue += 1.0 / self._objCount * objectNr

        #                 self._callback(progressValue)
        #             except Exception, e:
        #                 log.error(e)
        #     elif line.startswith('Print time:'):
        #         self._result._printTimeSeconds = int(line.split(':')[1].strip())
        #     elif line.startswith('Filament:'):
        #         self._result._filamentMM[0] = int(line.split(':')[1].strip())
        #         if profile.getMachineSetting('gcode_flavor') == 'UltiGCode':
        #             radius = profile.getProfileSettingFloat('filament_diameter') / 2.0
        #             self._result._filamentMM[0] /= (math.pi * radius * radius)
        #     elif line.startswith('Filament2:'):
        #         self._result._filamentMM[1] = int(line.split(':')[1].strip())
        #         if profile.getMachineSetting('gcode_flavor') == 'UltiGCode':
        #             radius = profile.getProfileSettingFloat('filament_diameter') / 2.0
        #             self._result._filamentMM[1] /= (math.pi * radius * radius)
        #     elif line.startswith('Replace:'):
        #         self._result._replaceInfo[line.split(':')[1].strip()] = line.split(':')[2].strip()
        #     else:
        #         self._result.addLog(line)
        #     line = stderr.readline()

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


class EngineRunner(QtCore.QObject):
    def __init__(self, scene, sceneview, engine):
        super(EngineRunner, self).__init__(sceneview)
        self.scene = scene
        self.engine = engine
        self.command_list = []
        self.model_hash = None

        self.setup()

        if self.obj_count > 0:
            self._thread = QtCore.QThread(sceneview._parent)
            worker = ProcessObserver(self._thread, self.command_list,
                    self.model_hash)
            worker.moveToThread(self._thread)
            QtCore.QObject.connect(self._thread, QtCore.SIGNAL('started()'), worker,
                    QtCore.SLOT('watchProcess()'))
            QtCore.QObject.connect(self._thread,
                    QtCore.SIGNAL('stop_process_sig(list)'), engine,
                    QtCore.SLOT('stopProcess(list)'))
            QtCore.QObject.connect(self._thread,
                    QtCore.SIGNAL('set_process_sig(list)'), engine,
                    QtCore.SLOT('setProcess(list)'))
            QtCore.QObject.connect(self._thread,
                    QtCore.SIGNAL('update_progress_sig(float)'), engine,
                    QtCore.SLOT('_callback(float)'))
            QtCore.QObject.connect(self._thread,
                    QtCore.SIGNAL('update_result_sig(EngineResult)'), engine,
                    QtCore.SLOT('updateResult(EngineResult)'))
            QtCore.QObject.connect(worker, QtCore.SIGNAL('finished()'), self._thread,
                    QtCore.SLOT('quit()'))
            QtCore.QObject.connect(worker, QtCore.SIGNAL('finished()'), worker,
                    QtCore.SLOT('deleteLater()'))
            QtCore.QObject.connect(self._thread, QtCore.SIGNAL('finished()'),
                    self._thread, QtCore.SLOT('deleteLater()'))
            print "starting thread"
            self._thread.start()
            print "started thread"

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
