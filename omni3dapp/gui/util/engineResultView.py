__copyright__ = "Copyright (C) 2013 David Braam - Released under terms of the AGPLv3 License"

import numpy
import math

import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GLU import *
from OpenGL.GL import *

from PySide import QtCore

from omni3dapp.util import profile
from omni3dapp.gui.util import openglHelpers
from omni3dapp.util.shortcuts import *


class EngineResultView(object):

    lineTypeList = [
        ('inset0',     'WALL-OUTER', [1, 0, 0, 1]),
        ('insetx',     'WALL-INNER', [0, 1, 0, 1]),
        ('openoutline', None,        [1, 0, 0, 1]),
        ('skin',       'FILL',       [1, 1, 0, 1]),
        ('infill',      None,        [1, 1, 0, 1]),
        ('support',    'SUPPORT',    [0, 1, 1, 1]),
        ('skirt',      'SKIRT',      [0, 1, 1, 1]),
        ('outline',     None,        [0, 0, 0, 1])
    ]

    def __init__(self, parent):
        self._parent = parent
        self._result = None
        self._enabled = False
        # self._gcodeLoadProgress = 0
        self._gcodeLayers = None
        self._layerVBOs = []
        self._layer20VBOs = []

        self.layerSelect = self._parent.mainwindow.qmlobject.findChild(
            QtCore.QObject, "layers_slider")

    def setResult(self, result):
        if self._result == result:
            return
        if result is None:
            self.setEnabled(False)

        self._result = result

        # Clean the saved VBO's
        for layer in self._layerVBOs:
            for typeName in layer.keys():
                self._parent.glReleaseList.append(layer[typeName])
        for layer in self._layer20VBOs:
            for typeName in layer.keys():
                self._parent.glReleaseList.append(layer[typeName])
        self._layerVBOs = []
        self._layer20VBOs = []

    def setEnabled(self, enabled):
        self._enabled = enabled
        self._parent.mainwindow.qmlobject.setLayersSliderVisible(int(enabled))

    @QtCore.Slot(dict)
    def _gcodeLoadCallback(self, attrs):
        result = attrs.get('result') or None
        progress = attrs.get('progress') or None
        layers = attrs.get('layers') or None
        if result != self._result:
            # Abort loading from this thread.
            return True

        self._gcodeLayers = layers
        self.setLayerSelectRange(len(layers))
        if len(layers) % 2 == 0:
            self._parent.setProgressBar(progress)
        return False

    def setLayerSelectRange(self, layers=None):
        if layers:
            self.layerSelect.setRange(0, layers - 1)
        elif self._result is not None and self._result._polygons is not None \
                and len(self._result._polygons) > 0:
            self.layerSelect.setRange(0, len(self._result._polygons) - 1)

    def getLayerNr(self):
        layerNr = int(self.layerSelect.getValue())
        if layerNr == self.layerSelect.getMaxValue() and \
                self._result is not None and len(self._result._polygons) > 0:
            layerNr = max(layerNr, len(self._result._polygons) - 1)
        return layerNr

    def getViewZ(self, layerNr):
        if len(self._result._polygons) > layerNr and \
                'inset0' in self._result._polygons[layerNr] and \
                len(self._result._polygons[layerNr]['inset0']) > 0 and \
                len(self._result._polygons[layerNr]['inset0'][0]) > 0:
            viewZ = self._result._polygons[layerNr]['inset0'][0][0][2]
        else:
            viewZ = layerNr * profile.getProfileSettingFloat('layer_height') +\
                profile.getProfileSettingFloat('bottom_thickness')
        return viewZ

    def renderLayer20VBOs(self, n, idx):
        while len(self._layer20VBOs) < idx + 1:
            self._layer20VBOs.append({})
        if self._result._polygons is not None and \
                n + 20 < len(self._result._polygons):
            layerVBOs = self._layer20VBOs[idx]
            for typeName, typeNameGCode, color in self.lineTypeList:
                allow = typeName in self._result._polygons[n + 19]
                if typeName == 'skirt':
                    for i in xrange(0, 20):
                        if typeName in self._result._polygons[n + i]:
                            allow = True
                if allow:
                    if typeName not in layerVBOs:
                        if self.generatedVBO:
                            continue
                        polygons = []
                        for i in xrange(0, 20):
                            if typeName in self._result._polygons[n+i]:
                                polygons += \
                                    self._result._polygons[n+i][typeName]
                        layerVBOs[typeName] = self._polygonsToVBO_lines(
                            polygons)
                        self.generatedVBO = True
                    glColor4f(color[0]*0.5, color[1]*0.5, color[2]*0.5,
                              color[3])
                    layerVBOs[typeName].render()

    def renderLayerVBOs(self, n, layerNr):
        c = 1.0 - (layerNr - n) * 0.05
        c = max(0.5, c)
        while len(self._layerVBOs) < n + 1:
            self._layerVBOs.append({})

        layerVBOs = self._layerVBOs[n]
        if self._gcodeLayers is not None and \
                ((layerNr - 9 < n < (len(self._gcodeLayers) - 1)) or
                 len(self._result._polygons) < 1):
            for typeNamePolygons, typeName, color in self.lineTypeList:
                if typeName is None:
                    continue
                if 'GCODE-' + typeName not in layerVBOs:
                    layerVBOs['GCODE-' + typeName] = self._gcodeToVBO_quads(
                        self._gcodeLayers[n+1:n+2], typeName)
                glColor4f(color[0]*c, color[1]*c, color[2]*c, color[3])
                layerVBOs['GCODE-' + typeName].render()

            if n == layerNr:
                if 'GCODE-MOVE' not in layerVBOs:
                    layerVBOs['GCODE-MOVE'] = self._gcodeToVBO_lines(
                        self._gcodeLayers[n+1:n+2])
                glColor4f(0, 0, c, 1)
                layerVBOs['GCODE-MOVE'].render()

        elif n < len(self._result._polygons):
            polygons = self._result._polygons[n]
            for typeName, typeNameGCode, color in self.lineTypeList:
                if typeName in polygons:
                    if typeName not in layerVBOs:
                        layerVBOs[typeName] = self._polygonsToVBO_lines(
                            polygons[typeName])
                    glColor4f(color[0]*c, color[1]*c, color[2]*c, color[3])
                    layerVBOs[typeName].render()

    def renderLayers(self, layerNr):
        n = layerNr
        self.generatedVBO = False

        while n >= 0:
            if layerNr - n >= 30 and n % 20 == 0 and \
                    len(self._result._polygons) > 0:
                self.renderLayer20VBOs(n, n/20)
                n -= 20
            else:
                self.renderLayerVBOs(n, layerNr)
                n -= 1

    def onDraw(self):
        if not self._enabled:
            return

        glPushMatrix()
        glEnable(GL_BLEND)
        if profile.getMachineSetting('machine_center_is_zero') != 'True':
            glTranslate(-profile.getMachineSettingFloat('machine_width') / 2,
                        -profile.getMachineSettingFloat('machine_depth') / 2,
                        0)
        glLineWidth(2)

        layerNr = self.getLayerNr()
        self._parent.viewTarget[2] = self.getViewZ(layerNr)

        if self._result is not None:
            self.generatedVBO = self.renderLayers(layerNr)

        glPopMatrix()
        if self.generatedVBO:
            pass
            # self._parent.queueRefresh()

    def _polygonsToVBO_lines(self, polygons):
        verts = numpy.zeros((0, 3), numpy.float32)
        indices = numpy.zeros((0), numpy.uint32)
        for poly in polygons:
            if len(poly) > 2:
                i = numpy.arange(len(verts), len(verts) + len(poly) + 1, 1,
                                 numpy.uint32)
                i[-1] = len(verts)
                i = numpy.dstack((i[0:-1], i[1:])).flatten()
            else:
                i = numpy.arange(len(verts), len(verts) + len(poly), 1,
                                 numpy.uint32)
            indices = numpy.concatenate((indices, i), 0)
            verts = numpy.concatenate((verts, poly), 0)
        return openglHelpers.GLVBO(GL_LINES, verts, indicesArray=indices)

    def _polygonsToVBO_quads(self, polygons):
        verts = numpy.zeros((0, 3), numpy.float32)
        indices = numpy.zeros((0), numpy.uint32)
        for poly in polygons:
            i = numpy.arange(len(verts), len(verts) + len(poly) + 1, 1,
                             numpy.uint32)
            i2 = numpy.arange(len(verts) + len(poly),
                              len(verts) + len(poly) + len(poly) + 1, 1,
                              numpy.uint32)
            i[-1] = len(verts)
            i2[-1] = len(verts) + len(poly)
            i = numpy.dstack((i[0:-1], i2[0:-1], i2[1:], i[1:])).flatten()
            indices = numpy.concatenate((indices, i), 0)
            verts = numpy.concatenate((verts, poly), 0)
            verts = numpy.concatenate(
                (verts, poly * numpy.array([1, 0, 1], numpy.float32) +
                    numpy.array([0, -100, 0], numpy.float32)),
                0)
        return openglHelpers.GLVBO(GL_QUADS, verts, indicesArray=indices)

    def _gcodeToVBO_quads(self, gcodeLayers, extrudeType):
        useFilamentArea = \
            profile.getMachineSetting('gcode_flavor') == 'UltiGCode'
        filamentRadius = \
            profile.getProfileSettingFloat('filament_diameter') / 2
        filamentArea = math.pi * filamentRadius * filamentRadius

        if ':' in extrudeType:
            extruder = int(extrudeType[extrudeType.find(':')+1:])
            extrudeType = extrudeType[0:extrudeType.find(':')]
        else:
            extruder = None

        verts = numpy.zeros((0, 3), numpy.float32)
        indices = numpy.zeros((0), numpy.uint32)
        for layer in gcodeLayers:
            for path in layer:
                if path['type'] == 'extrude' and \
                        path['pathType'] == extrudeType and \
                        (extruder is None or path['extruder'] == extruder):
                    a = path['points']
                    if extrudeType == 'FILL':
                        a[:, 2] += 0.01

                    # Construct the normals of each line 90deg
                    # rotated on the X/Y plane
                    normals = a[1:] - a[:-1]
                    lengths = numpy.sqrt(normals[:, 0]**2 + normals[:, 1]**2)
                    normals[:, 0], normals[:, 1] = -normals[:, 1] / lengths, \
                        normals[:, 0] / lengths
                    normals[:, 2] /= lengths

                    ePerDist = path['extrusion'][1:] / lengths
                    if useFilamentArea:
                        lineWidth = ePerDist / path['layerThickness'] / 2.0
                    else:
                        lineWidth = ePerDist * \
                            (filamentArea / path['layerThickness'] / 2)

                    normals[:, 0] *= lineWidth
                    normals[:, 1] *= lineWidth

                    b = numpy.zeros((len(a)-1, 0), numpy.float32)
                    b = numpy.concatenate((b, a[1:] + normals), 1)
                    b = numpy.concatenate((b, a[1:] - normals), 1)
                    b = numpy.concatenate((b, a[:-1] - normals), 1)
                    b = numpy.concatenate((b, a[:-1] + normals), 1)
                    b = b.reshape((len(b) * 4, 3))

                    i = numpy.arange(len(verts), len(verts) + len(b), 1,
                                     numpy.uint32)

                    verts = numpy.concatenate((verts, b))
                    indices = numpy.concatenate((indices, i))
        return openglHelpers.GLVBO(GL_QUADS, verts, indicesArray=indices)

    def _gcodeToVBO_lines(self, gcodeLayers):
        verts = numpy.zeros((0, 3), numpy.float32)
        indices = numpy.zeros((0), numpy.uint32)
        for layer in gcodeLayers:
            for path in layer:
                if path['type'] == 'move':
                    a = path['points'] + numpy.array([0, 0, 0.02],
                                                     numpy.float32)
                    i = numpy.arange(len(verts), len(verts) + len(a), 1,
                                     numpy.uint32)
                    i = numpy.dstack((i[0:-1], i[1:])).flatten()
                    verts = numpy.concatenate((verts, a))
                    indices = numpy.concatenate((indices, i))
                if path['type'] == 'retract':
                    a = path['points'] + numpy.array([0, 0, 0.02],
                                                     numpy.float32)
                    a = numpy.concatenate((a[:-1], a[1:] +
                                           numpy.array([0, 0, 1],
                                           numpy.float32)),
                                          1)
                    a = a.reshape((len(a) * 2, 3))
                    i = numpy.arange(len(verts), len(verts) + len(a), 1,
                                     numpy.uint32)
                    verts = numpy.concatenate((verts, a))
                    indices = numpy.concatenate((indices, i))
        return openglHelpers.GLVBO(GL_LINES, verts, indicesArray=indices)

    def set_selected_layer(self, val_mod):
        self.layerSelect.setValue(self.layerSelect.getValue() + val_mod)
        self._parent.queueRefresh()
        return True

    def onKeyChar(self, code, modifiers):
        if not self._enabled:
            return False
        # TODO: This is strange behaviour.
        # Overloaded functionality of keyboard buttons!
        if modifiers == SHIFT_KEY or modifiers == CTRL_KEY:
            if code == QtCore.Qt.Key_Up:
                self.set_selected_layer(1)
            elif code == QtCore.Qt.Key_Down:
                self.set_selected_layer(-1)
            elif code == QtCore.Qt.Key_PageUp:
                self.set_selected_layer(10)
            elif code == QtCore.Qt.Key_PageDown:
                self.set_selected_layer(-10)
        return False
