# -*- coding: utf-8 -*-
import os
import sys
import math
import time
import numpy
import traceback
import cStringIO as StringIO

from PySide import QtCore, QtGui

import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GLU import *
from OpenGL.GL import *

from omni3dapp.util import version
from omni3dapp.util import objectscene
from omni3dapp.util import profile
from omni3dapp.util import meshLoader
from omni3dapp.util import resources
from omni3dapp.util import sliceEngine
from omni3dapp.util.shortcuts import *

from omni3dapp.gui.util import previewTools
from omni3dapp.gui.util import engineResultView
from omni3dapp.gui.util import openglscene, openglHelpers
from omni3dapp.gui.util import containers

from omni3dapp.gui.tools import imageToMesh

from omni3dapp.logger import log


class SceneView(QtGui.QGraphicsScene):

    VIEW_MODES = ['normal', 'overhang', 'transparent', 'xray', 'gcode']

    setViewSelectOpacity = QtCore.Signal(float)

    def __init__(self, mainwindow=None, *args):
        super(SceneView, self).__init__(*args)
        self.mainwindow = mainwindow

        self.focus = None
        self.shownError = False
        self._machineSize = None
        self.objectShader = None
        self.platformTexture = None

        self.viewport = None
        self.modelMatrix = None
        self.projMatrix = None
        self.tempMatrix = None

        self.yaw = 30
        self.pitch = 60
        self.zoom = 300
        self.scene = objectscene.Scene()
        # self.viewTarget = numpy.array([0, 0, 0], numpy.float32)
        self.viewTarget = numpy.array([25, 25, 25], numpy.float32)
        self.animZoom = None

        self.objColors = [None, None, None, None]
        self.selectedObj = None
        self.focusObj = None

        self.mouseX = -1
        self.mouseY = -1
        self.mouseState = None
        self.mouse3Dpos = None

        self.viewMode = 'normal'

        self.animationList = []
        self.glReleaseList = []
        self.refreshQueued = False
        self.idleCalled = False

        self._layerOn = False

        self.platformMesh = {}

        self.tool = previewTools.toolNone(self)

        self.loadObjectShader()

        # self.printtemp_gauge = openglscene.glTempGauge(
        #     parent=self, size=(400, 10), pos=(0, -2), title="Heater:")
        # self.bedtemp_gauge = openglscene.glTempGauge(
        #     parent=self, size=(400, 10), pos=(0, -1), title="Bed:")

        # initialize temperatures targets
        self._printtemp = None
        self._bedtemp = None
        self._extr0temp = None
        self._heating = False

        self.engineResultView = engineResultView.EngineResultView(self)
        self.engine = sliceEngine.Engine(self, self.updateEngineProgress,
                                         self.engineResultView)

        self.slicing_finished = False

        self.progressBar = self.mainwindow.qmlobject.findChild(
            QtCore.QObject, "loader")
        self.bars = self.mainwindow.qmlobject.findChild(
            QtCore.QObject, "bars")
        self.bars.scaled.connect(self.onScaleEntry)

        self.idleTimer = QtCore.QTimer(self)
        self.idleTimer.timeout.connect(self.onIdle)
        self.idleTimer.start(0)

        self.updateProfileToControls()
        
        # TODO: move to place where the printer gets connected
        # self.tempGraphView = 

    def add(self, ctrl):
        if hasattr(self, 'container'):
            self.container.add(ctrl)

    @property
    def viewSelect(self):
        if not hasattr(self, 'view_select'):
            self.view_select = self.mainwindow.top_bar.findChild(
                QtCore.QObject, "view_modes")
        return self.view_select

    @property
    def topContainer(self):
        if not hasattr(self, '_topContainer'):
            dims = self.bars.getDimensions()
            self._topContainer = containers.Container(
                self, 0, 0, dims.get('width') or 0, dims.get('height') or 0)
        return self._topContainer

    def hasFocusTopBar(self):
        inputs = self.mainwindow.top_bar.findChildren(
            QtCore.QObject, QtCore.QRegExp(r'^text_input_\S+'))
        if any((inp.hasFocus() for inp in inputs)):
            return True
        return False

    def getObjectCenterPos(self):
        if self.selectedObj is None:
            return [0.0, 0.0, 0.0]
        pos = self.selectedObj.getPosition()
        size = self.selectedObj.getSize()
        return [pos[0], pos[1],
                size[2]/2 - profile.getProfileSettingFloat('object_sink')]

    def getObjectBoundaryCircle(self):
        if self.selectedObj is None:
            return 0.0
        return self.selectedObj.getBoundaryCircle()

    def getObjectSize(self):
        if self.selectedObj is None:
            return [0.0, 0.0, 0.0]
        return self.selectedObj.getSize()

    def getObjectMatrix(self):
        if self.selectedObj is None:
            return numpy.matrix(numpy.identity(3))
        return self.selectedObj.getMatrix()

    def getMouseRay(self, x, y):
        if self.viewport is None:
            return numpy.array([0, 0, 0], numpy.float32),\
                numpy.array([0, 0, 1], numpy.float32)
        p0 = openglHelpers.unproject(
            x, self.viewport[1] + self.viewport[3] - y, 0,
            self.modelMatrix, self.projMatrix, self.viewport)
        p1 = openglHelpers.unproject(
            x, self.viewport[1] + self.viewport[3] - y, 1,
            self.modelMatrix, self.projMatrix, self.viewport)
        p0 -= self.viewTarget
        p1 -= self.viewTarget
        return p0, p1

    def resetMachineSize(self):
        self._machineSize = None

    @property
    def machineSize(self):
        if self._machineSize is None:
            self._machineSize = numpy.array(profile.getMachineSizeList())
        return self._machineSize

    def selectObject(self, obj, zoom=True):
        if obj != self.selectedObj:
            self.selectedObj = obj
            self.updateModelSettingsToControls()
            self.updateToolButtons()
        if zoom and obj is not None:
            newZoom = obj.getBoundaryCircle() * 6
            if newZoom > numpy.max(self.machineSize) * 3:
                newZoom = numpy.max(self.machineSize) * 3
            self.animZoom = openglscene.animation(
                self, self.zoom, newZoom, 0.5)

    @QtCore.Slot()
    def selectRotateTool(self):
        self.tool = previewTools.toolRotate(self)

    @QtCore.Slot()
    def selectScaleTool(self):
        self.tool = previewTools.toolScale(self)

    @QtCore.Slot()
    def selectMirrorTool(self):
        self.tool = previewTools.toolNone(self)

    @QtCore.Slot()
    def onRotateReset(self):
        if self.selectedObj is None:
            return
        self.selectedObj.resetRotation()
        self.scene.pushFree(self.selectedObj)
        self.selectObject(self.selectedObj)
        self.sceneUpdated()

    @QtCore.Slot()
    def onLayFlat(self):
        if self.selectedObj is None:
            return
        self.selectedObj.layFlat()
        self.scene.pushFree(self.selectedObj)
        self.selectObject(self.selectedObj)
        self.sceneUpdated()

    @QtCore.Slot()
    def onScaleMax(self):
        if self.selectedObj is None:
            return
        machine = profile.getMachineSetting('machine_type')
        self.selectedObj.setPosition(numpy.array([0.0, 0.0]))
        self.scene.pushFree(self.selectedObj)
        if machine == "ultimaker2":
            #This is bad and Jaime should feel bad!
            self.selectedObj.setPosition(numpy.array([0.0, -10.0]))
            self.selectedObj.scaleUpTo(self.machineSize - numpy.array(
                profile.calculateObjectSizeOffsets() + [0.0],
                numpy.float32) * 2 - numpy.array([3,3,3], numpy.float32))
            self.selectedObj.setPosition(numpy.array([0.0,0.0]))
            self.scene.pushFree(self.selectedObj)
        else:
            self.selectedObj.setPosition(numpy.array([0.0, 0.0]))
            self.scene.pushFree(self.selectedObj)
            self.selectedObj.scaleUpTo(self.machineSize - numpy.array(
                profile.calculateObjectSizeOffsets() + [0.0],
                numpy.float32) * 2 - numpy.array([3,3,3], numpy.float32))
        self.scene.pushFree(self.selectedObj)
        self.selectObject(self.selectedObj)
        self.updateProfileToControls()
        self.sceneUpdated()

        self.bars.unsetActive()

    @QtCore.Slot(int)
    def onMirror(self, axis):
        if self.selectedObj is None:
            return
        self.selectedObj.mirror(axis)
        self.sceneUpdated()

    @QtCore.Slot(str, int, bool, bool)
    def onScaleEntry(self, value, axis, scale_uniform, is_mm=False):
        if self.selectedObj is None:
            return
        try:
            value = float(value)
        except (ValueError, TypeError), e:
            log.error("Error: {0}; could not scale.".format(e))
            return
        if is_mm:
            self.selectedObj.setSize(value, axis, scale_uniform)
        else:
            self.selectedObj.setScale(value, axis, scale_uniform)
        self.updateProfileToControls()
        self.scene.pushFree(self.selectedObj)
        self.selectObject(self.selectedObj)
        self.sceneUpdated()

    @QtCore.Slot()
    def getDimensionZ(self):
        return 123.0

    def loadObjectShader(self):
        if self.objectShader is not None:
            return

        if openglHelpers.hasShaderSupport():
            self.objectShader = openglHelpers.GLShader("""
                varying float light_amount;

                void main(void)
                {
                    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
                    gl_FrontColor = gl_Color;

                    light_amount = abs(
                        dot(normalize(gl_NormalMatrix * gl_Normal),
                        normalize(gl_LightSource[0].position.xyz)));
                    light_amount += 0.2;
                }
                                """, """
                varying float light_amount;

                void main(void)
                {
                    gl_FragColor = vec4(gl_Color.xyz * light_amount,
                                        gl_Color[3]);
                }
            """)
            self.objectOverhangShader = openglHelpers.GLShader("""
                uniform float cosAngle;
                uniform mat3 rotMatrix;
                varying float light_amount;

                void main(void)
                {
                    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
                    gl_FrontColor = gl_Color;

                    light_amount = abs(
                        dot(normalize(gl_NormalMatrix * gl_Normal),
                        normalize(gl_LightSource[0].position.xyz)));
                    light_amount += 0.2;
                    if (normalize(rotMatrix * gl_Normal).z < -cosAngle)
                    {
                        light_amount = -10.0;
                    }
                }
            """, """
                varying float light_amount;

                void main(void)
                {
                    if (light_amount == -10.0)
                    {
                        gl_FragColor = vec4(1.0, 0.0, 0.0, gl_Color[3]);
                    }else{
                        gl_FragColor = vec4(gl_Color.xyz * light_amount,
                                            gl_Color[3]);
                    }
                }
                                """)

        # Could not make shader.
        if self.objectShader is None or not self.objectShader.isValid():
            self.objectShader = openglHelpers.GLFakeShader()
            self.objectOverhangShader = openglHelpers.GLFakeShader()

    def setMouse3DPos(self):
        glFlush()
        n = glReadPixels(self.mouseX, self.height() - 1 - self.mouseY,
                         1, 1, GL_RGBA, GL_UNSIGNED_INT_8_8_8_8)[0][0] >> 8
        if n < len(self.scene.objects()):
            self.focusObj = self.scene.objects()[n]
        else:
            self.focusObj = None
        f = glReadPixels(self.mouseX, self.height() - 1 - self.mouseY,
                         1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)[0][0]
        self.mouse3Dpos = openglHelpers.unproject(
            self.mouseX, self.viewport[1] + self.viewport[3] - self.mouseY,
            f, self.modelMatrix, self.projMatrix, self.viewport)
        self.mouse3Dpos -= self.viewTarget

    def initializeGL(self):
        self.viewport = glGetIntegerv(GL_VIEWPORT)
        self.modelMatrix = glGetDoublev(GL_MODELVIEW_MATRIX)
        self.projMatrix = glGetDoublev(GL_PROJECTION_MATRIX)

        glClearColor(1, 1, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT |
                GL_STENCIL_BUFFER_BIT)

        glDisable(GL_STENCIL_TEST)
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)

    def init3DView(self):
        glLoadIdentity()

        glLightfv(GL_LIGHT0, GL_POSITION, [0.2, 0.2, 1.0, 0.0])

        glDisable(GL_RESCALE_NORMAL)
        glDisable(GL_LIGHTING)
        glDisable(GL_LIGHT0)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glDisable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glClearColor(0.2, 0.2, 0.2, 1.0)
        glClearStencil(0)
        glClearDepth(1.0)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = self.width() / self.height()
        gluPerspective(45.0, aspect, 1.0, numpy.max(self.machineSize) * 4)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT |
                GL_STENCIL_BUFFER_BIT)

    def renderObject(self, obj, brightness=0, addSink=True):
        if not obj:
            return

        glPushMatrix()
        if addSink:
            glTranslate(obj.getPosition()[0],
                        obj.getPosition()[1],
                        obj.getSize()[2] / 2 - profile.getProfileSettingFloat(
                            'object_sink')
                        )
        else:
            glTranslate(obj.getPosition()[0],
                        obj.getPosition()[1],
                        obj.getSize()[2] / 2)

        if self.tempMatrix is not None and obj == self.selectedObj:
            glMultMatrixf(openglHelpers.convert3x3MatrixTo4x4(self.tempMatrix))

        offset = obj.getDrawOffset()
        glTranslate(-offset[0], -offset[1], -offset[2] - obj.getSize()[2] / 2)

        glMultMatrixf(openglHelpers.convert3x3MatrixTo4x4(obj.getMatrix()))

        n = 0
        for mesh in obj._meshList:
            if mesh.vbo is None:
                mesh.vbo = openglHelpers.GLVBO(GL_TRIANGLES, mesh.vertexes,
                                               mesh.normal)
            if brightness != 0:
                glColor4fv(map(lambda idx: idx * brightness,
                           self.objColors[n]))
                n += 1
            mesh.vbo.render()
        glPopMatrix()

    def loadObject(self, obj):
        if obj._loadAnim is not None:
            if obj._loadAnim.isDone():
                obj._loadAnim = None
            else:
                return
        brightness = 1.0
        if self.focusObj == obj:
            brightness = 1.2
        elif self.focusObj is not None or \
                self.selectedObj is not None and \
                obj != self.selectedObj:
            brightness = 0.8

        if self.selectedObj == obj or self.selectedObj is None:
            # If we want transparent, then first render a solid black model
            # to remove the printer size lines.
            if self.viewMode == 'transparent':
                glColor4f(0, 0, 0, 0)
                self.renderObject(obj)
                glEnable(GL_BLEND)
                glBlendFunc(GL_ONE, GL_ONE)
                glDisable(GL_DEPTH_TEST)
                brightness *= 0.5
            if self.viewMode == 'xray':
                glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)
            glStencilOp(GL_INCR, GL_INCR, GL_INCR)
            glEnable(GL_STENCIL_TEST)

        if self.viewMode == 'overhang':
            if self.selectedObj == obj and self.tempMatrix is not None:
                self.objectOverhangShader.setUniform(
                    'rotMatrix', obj.getMatrix() * self.tempMatrix
                    )
            else:
                self.objectOverhangShader.setUniform(
                    'rotMatrix', obj.getMatrix()
                    )

        if not self.scene.checkPlatform(obj):
            glColor4f(0.5 * brightness, 0.5 * brightness, 0.5 * brightness,
                      0.8 * brightness)
            self.renderObject(obj)
        else:
            self.renderObject(obj, brightness)
        glDisable(GL_STENCIL_TEST)
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)

    def prepareViewMode(self):
        if self.viewMode == 'gcode':
            return
        glStencilFunc(GL_ALWAYS, 1, 1)
        glStencilOp(GL_INCR, GL_INCR, GL_INCR)

        if self.viewMode == 'overhang':
            self.objectOverhangShader.bind()
            self.objectOverhangShader.setUniform(
                'cosAngle',
                math.cos(math.radians(
                    90 - profile.getProfileSettingFloat('support_angle'))
                    )
                )
        else:
            self.objectShader.bind()

        for obj in self.scene.objects():
            self.loadObject(obj)

        if self.viewMode == 'xray':
            glPushMatrix()
            glLoadIdentity()
            glEnable(GL_STENCIL_TEST)
            glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP)  # Keep values
            glDisable(GL_DEPTH_TEST)
            for i in xrange(2, 15, 2):  # All even values
                glStencilFunc(GL_EQUAL, i, 0xFF)
                glColor(float(i)/10, float(i)/10, float(i)/5)
                glBegin(GL_QUADS)
                glVertex3f(-1000, -1000, -10)
                glVertex3f(1000, -1000, -10)
                glVertex3f(1000, 1000, -10)
                glVertex3f(-1000, 1000, -10)
                glEnd()
            for i in xrange(1, 15, 2):  # All odd values
                glStencilFunc(GL_EQUAL, i, 0xFF)
                glColor(float(i)/10, 0, 0)
                glBegin(GL_QUADS)
                glVertex3f(-1000, -1000, -10)
                glVertex3f(1000, -1000, -10)
                glVertex3f(1000, 1000, -10)
                glVertex3f(-1000, 1000, -10)
                glEnd()
            glPopMatrix()
            glDisable(GL_STENCIL_TEST)
            glEnable(GL_DEPTH_TEST)

        self.objectShader.unbind()
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)

    def loadGLTexture(self, filename):
        tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

        filepath = resources.getPathForImage(filename)
        img = QtGui.QImage(filepath)
        rgbData = ''.join([bit for bit in img.bits()])
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width(), img.height(), 0,
                     GL_BGRA, GL_UNSIGNED_INT_8_8_8_8_REV, rgbData)
        return tex

    def drawScene(self, painter):
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_LIGHTING)
        glColor4ub(255, 255, 255, 255)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width()-1, self.height()-1, 0, -1000.0, 1000.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def drawMachine(self):
        glEnable(GL_CULL_FACE)
        glEnable(GL_BLEND)

        size = self.machineSize

        glColor4f(0, 0, 0, 1)
        glLineWidth(4)
        glBegin(GL_LINES)
        glVertex3f(-size[0] / 2, -size[1] / 2, 0)
        glVertex3f(-size[0] / 2, -size[1] / 2, 10)
        glVertex3f(-size[0] / 2, -size[1] / 2, 0)
        glVertex3f(-size[0] / 2+10, -size[1] / 2, 0)
        glVertex3f(-size[0] / 2, -size[1] / 2, 0)
        glVertex3f(-size[0] / 2, -size[1] / 2+10, 0)
        glEnd()

        glDepthMask(False)

        polys = profile.getMachineSizePolygons()[0]
        height = size[2]

        # Color bottom
        glColor4f(0.25, 0.25, 0.25, 0.96)
        glBegin(GL_QUADS)
        for n in xrange(0, len(polys)):
            glVertex3f(polys[n][0], polys[n][1], 0)
        glEnd()

        glColor4f(0.5, 0.5, 0.5, 0.9)
        glLineWidth(1.5)

        # Draw grid on the bottom
        glBegin(GL_LINES)
        for step in xrange(0, int(size[1]), 10):
            glVertex3f(polys[0][0], polys[0][1] + step, 0)
            glVertex3f(polys[1][0], polys[1][1] + step, 0)

            glVertex3f(polys[0][0] + step, polys[0][1], 0)
            glVertex3f(polys[-1][0] + step, polys[-1][1], 0)
        glEnd()

        # Draw the build volume mesh
        # TODO: how should it look like for cicrular machine shape?
        # circular = profile.getMachineSetting('machine_shape') == 'Circular'
        glBegin(GL_LINES)
        for n in xrange(0, len(polys)):
            glVertex3f(polys[n][0], polys[n][1], height)
            glVertex3f(polys[n][0], polys[n][1], 0)

            glVertex3f(polys[n][0], polys[n][1], height)
            glVertex3f(polys[n-1][0], polys[n-1][1], height)
            glVertex3f(polys[n][0], polys[n][1], 0)
            glVertex3f(polys[n-1][0], polys[n-1][1], 0)

            glVertex3f(polys[n-1][0], polys[n-1][1], 0)
            glVertex3f(polys[n-1][0], polys[n-1][1], height)
        glEnd()

        # # Draw no-go zones. (clips in case of UM2)
        # glDisable(GL_TEXTURE_2D)
        # glColor4ub(127, 127, 127, 200)
        # for poly in polys[1:]:
        #     glBegin(GL_TRIANGLE_FAN)
        #     for p in poly:
        #         glTexCoord2f(p[0]/20, p[1]/20)
        #         glVertex3f(p[0], p[1], 0)
        #     glEnd()

        glDepthMask(True)
        glDisable(GL_BLEND)
        glDisable(GL_CULL_FACE)

    def drawBoxShadow(self):
        # Draw the object box-shadow, so you can see where it collides
        # with other objects.
        if self.selectedObj is not None:
            glEnable(GL_BLEND)
            glEnable(GL_CULL_FACE)
            glColor4f(0, 0, 0, 0.16)
            glDepthMask(False)
            for obj in self.scene.objects():
                glPushMatrix()
                glTranslatef(obj.getPosition()[0], obj.getPosition()[1], 0)
                glBegin(GL_TRIANGLE_FAN)
                for p in obj._boundaryHull[::-1]:
                    glVertex3f(p[0], p[1], 0)
                glEnd()
                glPopMatrix()
            if self.scene.isOneAtATime():  # Check print sequence mode.
                glPushMatrix()
                glColor4f(0, 0, 0, 0.06)
                glTranslatef(self.selectedObj.getPosition()[0],
                             self.selectedObj.getPosition()[1], 0)
                glBegin(GL_TRIANGLE_FAN)
                for p in self.selectedObj._printAreaHull[::-1]:
                    glVertex3f(p[0], p[1], 0)
                glEnd()
                glBegin(GL_TRIANGLE_FAN)
                for p in self.selectedObj._headAreaMinHull[::-1]:
                    glVertex3f(p[0], p[1], 0)
                glEnd()
                glPopMatrix()
            glDepthMask(True)
            glDisable(GL_CULL_FACE)

        # Draw the outline of the selected object on top
        # of everything else except the GUI.
        if self.selectedObj is not None and self.selectedObj._loadAnim is None:
            glDisable(GL_DEPTH_TEST)
            glEnable(GL_CULL_FACE)
            glEnable(GL_STENCIL_TEST)
            glDisable(GL_BLEND)
            glStencilFunc(GL_EQUAL, 0, 255)

            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            glLineWidth(4)
            glColor4f(1, 1, 1, 0.5)
            self.renderObject(self.selectedObj)
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

            # TODO: check if setting viewport is needed;
            # if so, fix error with wrong parameter types
            # glViewport(0, 0, self.width(), self.height())
            glDisable(GL_STENCIL_TEST)
            glDisable(GL_CULL_FACE)
            glEnable(GL_DEPTH_TEST)

        if self.selectedObj is not None:
            glPushMatrix()
            pos = self.getObjectCenterPos()
            glTranslate(pos[0], pos[1], pos[2])
            self.tool.onDraw()
            glPopMatrix()

    def queueRefresh(self):
        if self.idleCalled:
            self.update()
        else:
            self.refreshQueued = True

    def sceneUpdated(self):
        self.setProgressBar(0.0)
        self.cleanEngine()

        self.mainwindow.enablePrintButton(True)
        self.scene.updateSizeOffsets()
        self.queueRefresh()

    @QtCore.Slot()
    def reloadScene(self):
        fileList = []
        for obj in self.scene.objects():
            fileList.append(obj.getOriginFilename())
        self.onDeleteAll()

        self.startFilesLoader(fileList)

        self.bars.unsetActive()

    def isSlicingEnabled(self):
        return self.engine.isSlicingEnabled(self.scene)

    @QtCore.Slot()
    def onRunEngine(self):
        self.setInfoText(_("Slicing scene..."))
        self.engine.runEngine(self.scene)

    @QtCore.Slot()
    def onStopEngine(self, msg=None):
        self.engine.abortEngine()
        if msg:
            self.setInfoText(msg)
        self.mainwindow.setPrintState("IDLE")

    def onIdle(self):
        self.idleCalled = True
        if len(self.animationList) > 0 or self.refreshQueued:
            self.refreshQueued = False
            for anim in self.animationList:
                if anim.isDone():
                    self.animationList.remove(anim)
            self.update()

    def onPaint(self):
        self.init3DView()
        glTranslate(0.0, 0.0, -self.zoom)
        glRotate(-self.pitch, 1.0, 0.0, 0.0)
        glRotate(self.yaw, 0.0, 0.0, 1.0)
        glTranslate(-self.viewTarget[0],
                    -self.viewTarget[1],
                    -self.viewTarget[2])

        # TODO: sprawdzic czy potrzebne
        self.viewport = glGetIntegerv(GL_VIEWPORT)
        self.modelMatrix = glGetDoublev(GL_MODELVIEW_MATRIX)
        self.projMatrix = glGetDoublev(GL_PROJECTION_MATRIX)
        glClearColor(1, 1, 1, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT |
                GL_STENCIL_BUFFER_BIT)

        if self.viewMode != 'gcode':
            for n in xrange(0, len(self.scene.objects())):
                obj = self.scene.objects()[n]
                glColor4ub((n >> 16) & 0xFF, (n >> 8) & 0xFF, (n >> 0) & 0xFF,
                           0xFF)
                self.renderObject(obj)

        if self.mouseX > -1:  # mouse has not passed over the opengl window.
            self.setMouse3DPos()

        # TODO: sprawdzić czy potrzebne
        self.init3DView()
        glTranslate(0, 0, -self.zoom)
        glRotate(-self.pitch, 1, 0, 0)
        glRotate(self.yaw, 0, 0, 1)
        glTranslate(-self.viewTarget[0], -self.viewTarget[1],
                    -self.viewTarget[2])

        if self.objectShader is not None:
            self.objectShader.unbind()
        self.engineResultView.onDraw()

        self.prepareViewMode()
        self.drawMachine()
        if self.viewMode != 'gcode':
            self.drawBoxShadow()

        if self.viewMode == 'overhang' and not \
                openglHelpers.hasShaderSupport():
            glDisable(GL_DEPTH_TEST)
            glPushMatrix()
            glLoadIdentity()
            glTranslate(0, -4, -10)
            glColor4ub(60, 60, 60, 255)
            openglHelpers.glDrawStringCenter(
                _("Overhang view not working due to lack of OpenGL shaders \
                   support."))
            glPopMatrix()

    def paintGL(self, painter):
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        self.idleCalled = False

        try:
            for obj in self.glReleaseList:
                obj.release()
            renderStartTime = time.time()

            self.onPaint()

            self.drawScene(painter)

            glFlush()
            if version.isDevVersion():
                renderTime = time.time() - renderStartTime
                if renderTime == 0:
                    renderTime = 0.001
                glLoadIdentity()
                glTranslated(10.0, self.height() - 30.0, -1.0)
                glColor4f(0.2, 0.2, 0.2, 0.5)
                openglHelpers.glDrawStringLeft("fps:%d" % (1 / renderTime))
        except:
            # When an exception happens, catch it and show a message box.
            # If the exception is not caught the draw function bugs out.
            # Only show this exception once so we do not overload the user
            # with popups.
            if self.shownError:
                return
            errStr = _("An error has occurred during the 3D view drawing.")
            tb = traceback.extract_tb(sys.exc_info()[2])
            errStr += "\n%s: '%s'" % (str(sys.exc_info()[0].__name__),
                                      str(sys.exc_info()[1]))
            for n in xrange(len(tb)-1, -1, -1):
                locationInfo = tb[n]
                errStr += "\n @ %s:%s:%d" % (os.path.basename(locationInfo[0]),
                                             locationInfo[2], locationInfo[1])

            traceback.print_exc()
            log.error(errStr)
            # TODO: show modal box with error message
            # wx.CallAfter(wx.MessageBox, errStr, _("3D window error"),
            # wx.OK | wx.ICON_EXCLAMATION)
            self.shownError = True

    def drawBackground(self, painter, rect):
        # if painter.paintEngine().type() != QtGui.QPaintEngine.OpenGL2:
        #     QtCore.qWarning('OpenGLScene: drawBackground needs a QGLWidget '
        #                     + 'to be set as viewport on the '
        #                     + 'graphics view')
        #     return

        painter.beginNativePainting()

        self.initializeGL()
        self.paintGL(painter)

        painter.endNativePainting()

        QtCore.QTimer.singleShot(20, self.update)

    def updateProfileToControls(self):
        self.scene.arrangeAll()
        self.sceneUpdated()
        self.scene.updateSizeOffsets(True)
        self.objColors[0] = profile.getPreferenceColour('model_colour')
        self.objColors[1] = profile.getPreferenceColour('model_colour2')
        self.objColors[2] = profile.getPreferenceColour('model_colour3')
        self.objColors[3] = profile.getPreferenceColour('model_colour4')
        self.scene.updateMachineDimensions(self.machineSize)
        self.updateModelSettingsToControls()

    def updateModelSettingsToControls(self):
        if self.selectedObj is None:
            return
        scale = self.selectedObj.getScale()
        size = self.selectedObj.getSize()

        # Sets scales for scaleX, scaleY, scaleZ, sizeY, sizewY, sizeZ
        self.bars.setScales(round(scale[0], 2), round(scale[1], 2),
            round(scale[2], 2), round(size[0], 2), round(size[1], 2),
            round(size[2], 2))

    def updateToolButtons(self):
        enabled = not (self.selectedObj is None)

        self.mainwindow.top_bar.enableObjectTools(enabled)

    def updateEngineProgress(self, progressValue):
        self.progressBar.setValue(progressValue)

        if progressValue >= 1:
            self.setPrintingInfo()
            self.mainwindow.setPrintState("SLICED")
            enablePrinting = self.mainwindow.isOnline()
            self.mainwindow.enablePrintButton(enablePrinting)
            self.setInfoText(enablePrinting and "" or _("Not connected to printer"))

        self.queueRefresh()

    def setPrintingInfo(self):
        result = self.engine.getResult()
        self.slicing_finished = result is not None and result.isFinished()
        if not self.slicing_finished:
            return

        time_info = "{0}".format(result.getPrintTime())
        params_info = ""
        for e in xrange(0, int(profile.getMachineSetting(
                               'extruder_amount'))):
            amount = result.getFilamentAmount(e)
            if amount is None:
                continue
            params_info += "{0}".format(amount)
            # cost = result.getFilamentCost(e)
            # if cost is not None:
            #     params_info += " {0}".format(cost)

        self.mainwindow.setPrintButton(time_info, params_info)

    def onCenter(self):
        if self.focusObj is None:
            return
        self.focusObj.setPosition(numpy.array([0.0, 0.0]))
        self.scene.pushFree(self.selectedObj)
        self.sceneUpdated()

    def onMultiply(self):
        if self.focusObj is None:
            return
        obj = self.focusObj
        cnt, res = QtGui.QInputDialog.getInteger(
            self.mainwindow, _("Multiply"), _("Number of copies"), 1, 1, 100)
        if not res:
            return
        n = 0
        while True:
            n += 1
            newObj = obj.copy()
            self.scene.add(newObj)
            self.scene.centerAll()
            if not self.scene.checkPlatform(newObj):
                break
            if n > cnt:
                break
        if n <= cnt:
            pass
            # TODO: create notofication popups (as what instead of popup)
            # self.notification.message("Could not create more than %d \
            #         items" % (n - 1))
        self.scene.remove(newObj)
        self.scene.centerAll()
        self.sceneUpdated()

    def onSplitObject(self):
        log.debug("Not implemented yet")
        pass
        # TODO: implement splitting object
        # if self.focusObj is None:
        #     return
        # self.scene.remove(self.focusObj)
        # for obj in self.focusObj.split(self.splitCallback):
        #     if numpy.max(obj.getSize()) > 2.0:
        #         self.scene.add(obj)
        # self.scene.centerAll()
        # self.selectObject(None)
        # self.sceneUpdated()

    def onMergeObjects(self):
        # TODO: test the implementation of merging objects
        log.debug("Not implemented yet")
        # if self.selectedObj is None or self.focusObj is None \
        #         or self.selectedObj == self.focusObj:
        #     if len(self.scene.objects()) == 2:
        #         self.scene.merge(self.scene.objects()[0],
        #                 self.scene.objects()[1])
        #         self.sceneUpdated()
        #     return
        # self.scene.merge(self.selectedObj, self.focusObj)
        # self.sceneUpdated()

    @QtCore.Slot()
    def onDeleteAll(self):
        while len(self.scene.objects()) > 0:
            self.onDeleteObject(self.scene.objects()[0])
        self.cleanResult()

    def onDeleteObject(self, obj=None):
        if not obj:
            obj = self.focusObj
        if obj == self.selectedObj:
            self.selectObject(None)
        if obj == self.focusObj:
            self.focusObj = None
        self.scene.remove(obj)
        for mesh in obj._meshList:
            if mesh.vbo is not None and mesh.vbo.decRef():
                self.glReleaseList.append(mesh.vbo)
        if len(self.scene.objects()) == 0:
            self.cleanResult()
        import gc
        gc.collect()
        self.sceneUpdated()

    def hideLayersButton(self):
        self.viewSelect.hideLayersButton()

    def showLayersButton(self):
        self.viewSelect.showLayersButton()

    def cleanEngine(self):
        self.onStopEngine()
        self.engineResultView.setResult(None)
        self.engineResultView.setLayers(None)
        self.mainwindow.setPrintButton("", "")
        self.hideLayersButton()

    def cleanResult(self):
        self.cleanEngine()
        self.setViewMode('normal')
        self.viewSelect.setEnabled(False)

    def createContextMenu(self, evt):
        menu = QtGui.QMenu()
        if self.focusObj is not None:
            menu.addAction(QtGui.QAction(_("Center on platform"), menu,
                           triggered=self.onCenter))
            menu.addAction(QtGui.QAction(_("Delete object"), menu,
                           triggered=self.onDeleteObject))
            menu.addAction(QtGui.QAction(_("Multiply object"), menu,
                           triggered=self.onMultiply))
            menu.addAction(QtGui.QAction(_("Split object into parts"), menu,
                           triggered=self.onSplitObject))

        if ((self.selectedObj != self.focusObj and
            self.focusObj is not None) or
            len(self.scene.objects()) == 2) and \
                int(profile.getMachineSetting('extruder_amount')) > 1:
            menu.addAction(QtGui.QAction(_("Dual extrusion merge"),
                           menu, triggered=self.onMergeObjects))

        if len(self.scene.objects()) > 0:
            menu.addAction(QtGui.QAction(_("Delete all objects"), menu,
                           triggered=self.onDeleteAll))
            menu.addAction(QtGui.QAction(_("Reload all objects"), menu,
                           triggered=self.reloadScene))

        if not menu.isEmpty():
            pos = evt.screenPos()
            menu.exec_(QtCore.QPoint(pos.x(), pos.y()))

    def wheelEvent(self, evt):
        pos = evt.scenePos()
        if self.topContainer.mousePressEvent(pos.x(), pos.y()) or \
                self._layerOn:
                    return

        delta = evt.delta()
        delta = delta/abs(delta)
        self.zoom *= 1.0 - delta / 10.0
        if self.zoom < 1.0:
            self.zoom = 1.0
        if self.zoom > numpy.max(self.machineSize) * 3:
            self.zoom = numpy.max(self.machineSize) * 3
        self.update()

    def guiMouseMoveEvent(self, evt):
        self.update()
        pos = evt.scenePos()
        if hasattr(self, 'container'):
            self.container.onMouseMoveEvent(pos.x(), pos.y())

    def mousePressEvent(self, evt):
        self.setFocus()
        pos = evt.scenePos()

        if not self.topContainer.mousePressEvent(pos.x(), pos.y()) and not \
                self._layerOn:
            self.onMouseDown(evt)

        super(SceneView, self).mousePressEvent(evt)

    def mouseDoubleClickEvent(self, evt):
        self.mouseState = 'doubleClick'

    def mouseReleaseEvent(self, evt):
        pos = evt.scenePos()
        if not self.topContainer.mouseReleaseEvent(pos.x(), pos.y()) and not \
                self._layerOn:
            self.onMouseUp(evt)

        super(SceneView, self).mouseReleaseEvent(evt)

    def onMouseDown(self, evt):
        pos = evt.scenePos()
        self.mouseX = pos.x()
        self.mouseY = pos.y()
        self.mouseClick3DPos = self.mouse3Dpos
        self.mouseClickFocus = self.focusObj

        if self.mouseState == 'dragObject' and self.selectedObj is not None:
            self.scene.pushFree(self.selectedObj)
            self.sceneUpdated()
        self.mouseState = 'dragOrClick'

        p0, p1 = self.getMouseRay(self.mouseX, self.mouseY)
        p0 -= self.getObjectCenterPos() - self.viewTarget
        p1 -= self.getObjectCenterPos() - self.viewTarget
        if self.tool.onDragStart(p0, p1):
            self.mouseState = 'tool'
        if self.mouseState == 'dragOrClick' and evt.buttons() == LEFT_BUTTON \
                and self.focusObj is not None:
                    self.selectObject(self.focusObj, False)
                    self.queueRefresh()

    def onMouseUp(self, evt):
        curr_buttons = evt.buttons()
        last_button = evt.button()
        if not curr_buttons == NO_BUTTON:
            return
        if self.mouseState == 'dragOrClick':
            if last_button == LEFT_BUTTON:
                self.selectObject(self.focusObj)
            elif last_button == RIGHT_BUTTON:
                self.createContextMenu(evt)
        elif self.mouseState == 'dragObject' and self.selectedObj is not None:
            self.scene.pushFree(self.selectedObj)
            self.sceneUpdated()
        elif self.mouseState == 'tool':
            if self.tempMatrix is not None and self.selectedObj is not None:
                self.selectedObj.applyMatrix(self.tempMatrix)
                self.scene.pushFree(self.selectedObj)
                self.selectObject(self.selectedObj)
            self.tempMatrix = None
            self.tool.onDragEnd()
            self.updateModelSettingsToControls()
            self.sceneUpdated()
        self.mouseState = None

    def mouseMoveEvent(self, evt):
        pos = evt.scenePos()
        x, y = pos.x(), pos.y()
        if self.topContainer.mouseMoveEvent(x, y) or self._layerOn:
            super(SceneView, self).mouseMoveEvent(evt)
            return

        p0, p1 = self.getMouseRay(x, y)
        p0 -= self.getObjectCenterPos() - self.viewTarget
        p1 -= self.getObjectCenterPos() - self.viewTarget

        buttons = evt.buttons()
        if buttons != NO_BUTTON and self.mouseState is not None:
            if self.mouseState == 'tool':
                self.tool.onDrag(p0, p1, evt)
            elif buttons == RIGHT_BUTTON:
                self.mouseState = 'drag'
                if evt.modifiers() == SHIFT_KEY:
                    a = math.cos(math.radians(self.yaw)) / 3.0
                    b = math.sin(math.radians(self.yaw)) / 3.0
                    self.viewTarget[0] += float(x - self.mouseX) * -a
                    self.viewTarget[1] += float(x - self.mouseX) * b
                    self.viewTarget[0] += float(y - self.mouseY) * b
                    self.viewTarget[1] += float(y - self.mouseY) * a
                else:
                    self.yaw += x - self.mouseX
                    self.pitch -= y - self.mouseY
                if self.pitch > 170:
                    self.pitch = 170
                if self.pitch < 10:
                    self.pitch = 10
            elif buttons == MIDDLE_BUTTON or \
                    buttons == (RIGHT_BUTTON or LEFT_BUTTON):
                self.mouseState = 'drag'
                self.zoom += y - self.mouseY
                if self.zoom < 1:
                    self.zoom = 1
                if self.zoom > numpy.max(self.machineSize) * 3:
                    self.zoom = numpy.max(self.machineSize) * 3
            elif buttons == LEFT_BUTTON and self.selectedObj is not None and \
                    self.selectedObj == self.mouseClickFocus:
                self.mouseState = 'dragObject'
                z = max(0, self.mouseClick3DPos[2])
                p0, p1 = self.getMouseRay(self.mouseX, self.mouseY)
                p2, p3 = self.getMouseRay(x, y)
                p0[2] -= z
                p1[2] -= z
                p2[2] -= z
                p3[2] -= z
                cursorZ0 = p0 - (p1 - p0) * (p0[2] / (p1[2] - p0[2]))
                cursorZ1 = p2 - (p3 - p2) * (p2[2] / (p3[2] - p2[2]))
                diff = cursorZ1 - cursorZ0
                self.selectedObj.setPosition(
                    self.selectedObj.getPosition() + diff[0:2])
        if buttons == NO_BUTTON or self.mouseState != 'tool':
            self.tool.onMouseMove(p0, p1)

        self.mouseX = x
        self.mouseY = y

        self.guiMouseMoveEvent(evt)

        super(SceneView, self).mouseMoveEvent(evt)

    def keyPressEvent(self, evt):
        if self.topContainer.keyPressEvent() or self._layerOn:
            super(SceneView, self).keyPressEvent(evt)
            return

        code = evt.key()
        modifiers = evt.modifiers()
        if self.engineResultView.onKeyChar(code, modifiers) or \
                (hasattr(self, 'container') and
                 self.container.keyPressEvent(code, modifiers)):
            self.queueRefresh()
            return
        if code == QtCore.Qt.Key_Delete or \
                (code == QtCore.Qt.Key_Backspace and
                 sys.platform.startswith("darwin")):
            if self.selectedObj is not None:
                self.onDeleteObject(self.selectedObj)
                self.queueRefresh()
        if code == QtCore.Qt.Key_Up:
            if modifiers == SHIFT_KEY:
                self.zoom /= 1.2
                if self.zoom < 1:
                    self.zoom = 1
            else:
                self.pitch -= 15
            self.queueRefresh()
        elif code == QtCore.Qt.Key_Down:
            if modifiers == SHIFT_KEY:
                self.zoom *= 1.2
                if self.zoom > numpy.max(self.machineSize) * 3:
                    self.zoom = numpy.max(self.machineSize) * 3
            else:
                self.pitch += 15
            self.queueRefresh()
        elif code == QtCore.Qt.Key_Left:
            self.changeCamera(yaw=self.yaw-15)
        elif code == QtCore.Qt.Key_Right:
            self.changeCamera(yaw=self.yaw+15)
        elif evt.text == QtCore.Qt.Key_Plus:
            self.zoom /= 1.2
            if self.zoom < 1:
                self.zoom = 1
            self.queueRefresh()
        elif code == QtCore.Qt.Key_Minus:
            self.zoom *= 1.2
            if self.zoom > numpy.max(self.machineSize) * 3:
                self.zoom = numpy.max(self.machineSize) * 3
            self.queueRefresh()
        elif code == QtCore.Qt.Key_Home:
            self.changeCamera(yaw=30, pitch=60)
        elif code == QtCore.Qt.Key_PageUp:
            self.changeCamera(yaw=0, pitch=0)
        elif code == QtCore.Qt.Key_PageDown:
            self.changeCamera(yaw=0, pitch=90)
        elif code == QtCore.Qt.Key_End:
            self.changeCamera(yaw=90, pitch=90)

        # if code == QtCore.Qt.Key_F3 and modifiers == SHIFT_KEY:
        #     ShaderEditor(self, self.shaderUpdate,
        #             self.objectLoadShader.getVertexShader(),
        #             self.objectLoadShader.getFragmentShader())

    def changeCamera(self, yaw=None, pitch=None):
        if yaw is not None:
            self.yaw = yaw
        if pitch is not None:
            self.pitch = pitch
        self.queueRefresh()

    def loadGCodeFile(self, filename):
        self.setInfoText(_("Loading GCode..."))
        self.onDeleteAll()
        # Cheat the engine results to load a GCode file into it.
        self.engine.abortEngine()
        self.engine._result = sliceEngine.EngineResult(self)

        with open(filename, "rU") as f:
            self.engine._result.setGCode(f.read())

        self.engine._result.setFinished(True)
        self.engineResultView.setResult(self.engine._result)

        self.mainwindow.setPrintState("SLICED")
        self.mainwindow.qmlobject.setPrintButtonVisible(1)

        self.showLayersButton()
        self.setViewMode('gcode')

    def loadingLayersFinished(self):
        self.slicing_finished = True
        if self.mainwindow.isOnline():
            self.mainwindow.enablePrintButton(True)
            self.queueRefresh()


    @QtCore.Slot(str)
    def setViewMode(self, viewmode='normal'):
        if viewmode not in self.VIEW_MODES:
            log.error("Trying to set undefined view mode: {0}".format(
                viewmode))
            return
        self.viewMode = viewmode
        if viewmode == 'gcode':
            self.tool = previewTools.toolNone(self)
            self.loadLayers()
        self.engineResultView.setEnabled(self.viewMode=='gcode')
        self.queueRefresh()

    def setPrintingGcode(self, gcode):
        self.mainwindow.setPrintingGcode(gcode)

    def setSlicingFinished(self):
        self.slicing_finished = True
        self.showLayersButton()

    def loadLayers(self, printing=False):
        result = self.engine.getResult()
        if result._gcodeInterpreter.layerList:
            if printing:
                self.startPrinting(result.getGCode())
            return
        result.generateGCodeLayers(self.engineResultView, printing)

    def isPrintingEnabled(self):
        return self.slicing_finished and self.mainwindow.isOnline()

    @QtCore.Slot()
    def enablePrinting(self):
        if self.isPrintingEnabled() and \
                self.mainwindow.print_button.getState() == "SLICED":
            self.mainwindow.enablePrintButton(True)
            self.update()

    @QtCore.Slot(float)
    def setPrinttempTarget(self, temp):
        self._printtemp = temp
        # self.printtemp_gauge.setTarget(temp)

    @QtCore.Slot(float)
    def setBedtempTarget(self, temp):
        self._bedtemp = temp
        # self.bedtemp_gauge.setTarget(temp)

    def setHeatingFinished(self):
        self._heating = False
        self.progressBar.setValue(0)
        self.setInfoText(_("Printing..."))
        # self.mainwindow.pc.heating_finished()
        self.mainwindow.setHeatingFinished()
        # self.mainwindow.pc.startprint()

    def setHeatingStarted(self):
        self._heating = True

    @QtCore.Slot(float, float)
    def setTempProgress(self, printtemp, bedtemp):
        if not (self._heating and (self._printtemp or self._bedtemp)):
            return

        self.setInfoText(
            _("Heating up... <Temperatures: extruder {0}/{1}, bed {2}/{3}>".format(
              printtemp, self._printtemp, bedtemp, self._bedtemp)))

        if printtemp:
            printtemp /= self._printtemp

        if bedtemp:
            bedtemp /= self._bedtemp

        val = min(printtemp, bedtemp)
        if not val:
            val = printtemp or bedtemp

        self.progressBar.setValue(val or 0)

        if val >= 1.0:
            self.setHeatingFinished()

    @QtCore.Slot(float)
    def setPrinttempValue(self, temp):
        pass
        # self.printtemp_gauge.setValue(temp)

    @QtCore.Slot(float)
    def setBedtempValue(self, temp):
        pass
        # self.bedtemp_gauge.setValue(temp)

    @QtCore.Slot(float)
    def setExtr0TempTarget(self, temp):
        self._extr0temp = temp
        pass

    def onEndprint(self):
        self.mainwindow.setPrintState("SLICED")
        self.setInfoText(_("Printing finished"))

    @QtCore.Slot()
    def onPrintButton(self):
        self.loadLayers(printing=True)

    def startPrinting(self, gcode):
        self.mainwindow.pc.printfile(gcode)

    @QtCore.Slot()
    def showLoadModel(self):
        img_extentions = imageToMesh.supportedExtensions()
        mesh_extentions = meshLoader.loadSupportedExtensions()

        wildcard_filter = ';;'.join([
            "All ({0})",
            "Mesh files ({1})",
            "Image files ({2})",
            "GCode files ({3})"]).format(
                ' '.join(map(lambda s: '*' + s,
                             mesh_extentions + img_extentions +
                             ['.g', '.gcode'])),
                ' '.join(map(lambda s: '*' + s, mesh_extentions)),
                ' '.join(map(lambda s: '*' + s, img_extentions)),
                ' '.join(map(lambda s: '*' + s, ['.g', '.gcode'])))

        file_dialog = QtGui.QFileDialog(
            self.mainwindow,
            _("Open 3D model"),
            os.path.split(profile.getPreference('lastFile'))[0],
            wildcard_filter)
        file_dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)

        if file_dialog.exec_():
            filenames = file_dialog.selectedFiles()
        else:
            return False

        if len(filenames) < 1:
            return False

        self.setViewMode('normal')

        profile.putPreference('lastFile', filenames[0])

        self.startFilesLoader(filenames)

    def startFilesLoader(self, filenames):
        self.files_loader = FilesLoader(self, filenames, self.machineSize)
        self.files_loader_thread = QtCore.QThread(self.mainwindow)
        self.files_loader.moveToThread(self.files_loader_thread)
        self.files_loader_thread.started.connect(self.files_loader.loadFiles)
        self.files_loader.load_gcode_file_sig.connect(self.loadGCodeFile)
        self.files_loader.update_scene_sig.connect(
            self.updateProfileToControls)
        self.files_loader.set_progressbar_sig.connect(self.setProgressBar)
        self.files_loader.object_loaded_sig.connect(self.afterObjectLoaded)
        self.files_loader.set_info_text_sig.connect(self.setInfoText)

        self.files_loader.finished.connect(self.files_loader_thread.quit)
        self.files_loader.finished.connect(self.files_loader.deleteLater)
        self.files_loader_thread.finished.connect(
            self.files_loader_thread.deleteLater)

        self.files_loader_thread.start()

    @QtCore.Slot()
    def afterObjectLoaded(self):
        self.viewSelect.setOptionEnabled(True)
        self.mainwindow.setPrintState("IDLE")
        self.mainwindow.qmlobject.setPrintButtonVisible(1)

    @QtCore.Slot(float)
    def setProgressBar(self, value):
        self.progressBar.setValue(value)
        if value == 1:
            self.setInfoText("")
        self.queueRefresh()

    @QtCore.Slot(str)
    def setInfoText(self, text):
        self.progressBar.setInfoText(text)
        self.queueRefresh()

    @QtCore.Slot()
    def showSaveModel(self):
        if len(self.scene.objects()) < 1:
            self.setInfoText(
                _("There are no objects on the scene to be saved."))
            return

        file_extentions = meshLoader.saveSupportedExtensions()

        wildcard_filter = "Mesh files ({0})".format(
            ' '.join(map(lambda s: '*' + s, file_extentions)))

        chosen = QtGui.QFileDialog.getSaveFileName(
            self.mainwindow,
            _("Save 3D model"),
            os.path.split(profile.getPreference('lastFile'))[0],
            wildcard_filter)

        filename, used_filter = chosen
        if filename:
            meshLoader.saveMeshes(filename, self.scene.objects())
            self.setInfoText(_("Saved scene as {0}".format(filename)))

    @QtCore.Slot()
    def showSaveGCode(self):
        if len(self.scene._objectList) < 1:
            self.setInfoText(
                _("There are no objects on the scene to be saved."))
            return

        result = self.engine.getResult()
        if not result or not result.isFinished():
            self.setInfoText(_("GCode is not generated yet, "
                               "you cannot save it"))
            return

        wildcard_filter = "Toolpath ({0})".format(
            '*' + profile.getGCodeExtension())

        chosen = QtGui.QFileDialog.getSaveFileName(
            self.mainwindow,
            _("Save toolpath"),
            os.path.dirname(profile.getPreference('lastFile')),
            wildcard_filter)

        filename, used_filter = chosen
        if filename:
            self.save_gcode_worker = SaveGCodeWorker(self.engine, filename)
            self.save_gcode_thread = QtCore.QThread(self.mainwindow)
            self.save_gcode_worker.moveToThread(self.save_gcode_thread)

            self.save_gcode_thread.started.connect(
                self.save_gcode_worker.saveGCode)
            self.save_gcode_worker.set_progress_bar_sig.connect(
                self.setProgressBar)
            self.save_gcode_worker.notification_sig.connect(self.setInfoText)

            self.save_gcode_worker.finished.connect(
                self.save_gcode_thread.quit)
            self.save_gcode_worker.finished.connect(
                self.save_gcode_worker.deleteLater)
            self.save_gcode_thread.finished.connect(
                self.save_gcode_thread.deleteLater)

            self.save_gcode_thread.start()

    @QtCore.Slot()
    def setLayerOn(self):
        self._layerOn = True

    @QtCore.Slot()
    def setLayerOff(self):
        self._layerOn = False


class FilesLoader(QtCore.QObject):
    load_gcode_file_sig = QtCore.Signal(str)
    update_scene_sig = QtCore.Signal()
    set_progressbar_sig = QtCore.Signal(float)
    set_info_text_sig = QtCore.Signal(str)
    object_loaded_sig = QtCore.Signal()
    finished = QtCore.Signal()

    def __init__(self, sceneview, filenames, machine_size):
        super(FilesLoader, self).__init__()
        self.sceneview = sceneview
        self.filenames = filenames
        self.machine_size = machine_size

    def loadFiles(self):
        main_window = self.sceneview.mainwindow
        # only one GCODE file can be active
        # so if single gcode file, process this
        # otherwise ignore all gcode files
        if len(self.filenames) == 1:
            filename = self.filenames[0]
            ext = os.path.splitext(filename)[1].lower()
            if ext in ['.g', '.gcode']:
                # main_window.add_to_model_mru(filename)
                self.load_gcode_file_sig.emit(filename)
                self.finished.emit()
                return
        # process directories and special file types
        # and keep scene files for later processing
        self.loadMultipleFiles()

        self.finished.emit()

    def loadMultipleFiles(self):
        scene_filenames = []
        ignored_types = dict()
        # use file list as queue
        # pop first entry for processing and append new files at end
        while self.filenames:
            filename = self.filenames.pop(0)
            if os.path.isdir(filename):
                # directory: queue all included files and directories
                self.filenames.extend(os.path.join(filename, f)
                                      for f in os.listdir(filename))
            else:
                ext = os.path.splitext(filename)[1].lower()
                if ext == '.ini':
                    profile.loadProfile(filename)
                    # main_window.addToProfileMRU(filename)
                elif ext in meshLoader.loadSupportedExtensions() or \
                        ext in imageToMesh.supportedExtensions():
                    scene_filenames.append(filename)
                    # main_window.add_to_model_mru(filename)
                else:
                    ignored_types[ext] = 1
        if ignored_types:
            ignored_types = ignored_types.keys()
            ignored_types.sort()
            # TODO: add notofication
            # self.notification.message(
            #     "ignored: " + " ".join("*" + type for type in ignored_types))

        # now process all the scene files
        if scene_filenames:
            self.loadScene(scene_filenames)
            self.sceneview.selectObject(None)
            newZoom = numpy.max(self.machine_size)
            self.sceneview.animZoom = openglscene.animation(
                self.sceneview, self.sceneview.zoom, newZoom, 0.5)

    def loadScene(self, filelist):
        flen = len(filelist)
        fraction = 1.0 / flen
        for no, filename in enumerate(filelist):
            # Set info text about loading a file
            self.set_info_text_sig.emit(
                _("Loading file {0} out of {1}: {2}".format(
                    no+1, flen, filename)))
            self.loadFileOntoScene(
                filename, lambda val: self.set_progressbar_sig.emit(
                    (no+val)*fraction)
                )
        self.update_scene_sig.emit()

    def loadFileOntoScene(self, filename, callback):
        try:
            ext = os.path.splitext(filename)[1].lower()
            if ext in imageToMesh.supportedExtensions():
                # TODO: implement converting images (do we need that?)
                # imageToMesh.convertImageDialog(self, filename).Show()
                objList = []
            else:
                objList = meshLoader.loadMeshes(filename, callback)
        except Exception, e:
            traceback.print_exc()
            log.error(e)
        else:
            self.loadObjectsOntoScene(objList)
            self.set_progressbar_sig.emit(1.0)
            time.sleep(0.1)
            self.object_loaded_sig.emit()

    def loadObjectsOntoScene(self, objList):
        scene = self.sceneview.scene
        for obj in objList:
            scene.add(obj)
            if not scene.checkPlatform(obj):
                scene.centerAll()
            self.sceneview.selectObject(obj)
            if obj.getScale()[0] < 1.0:
                self.sceneview.setInfoText(_("Warning: Object scaled down"))


class SaveGCodeWorker(QtCore.QObject):
    set_progress_bar_sig = QtCore.Signal(float)
    notification_sig = QtCore.Signal(str)
    finished = QtCore.Signal()

    def __init__(self, engine, target, eject_drive=False):
        super(SaveGCodeWorker, self).__init__()
        self.engine = engine
        self.target = target
        self.eject_drive = eject_drive

    def saveGCode(self):
        data = self.engine.getResult().getGCode()
        try:
            size = float(len(data))
            fsrc = StringIO.StringIO(data)
            with open(self.target, 'wb') as fdst:
                while 1:
                    buf = fsrc.read(16*1024)
                    if not buf:
                        break
                    fdst.write(buf)
                    self.set_progress_bar_sig.emit(float(fsrc.tell()) / size)
        except Exception, e:
            log.error(e)
            self.notification_sig.emit("Failed to save file")
            self.finished.emit()
        else:
            self.notification_sig.emit(_("Saved as {0}".format(self.target)))
            # if eject_drive:
            #     # self.notification.message("Saved as %s" % (targetFilename),
            # lambda : self._doEjectSD(ejectDrive), 31, 'Eject')
            #     print "Saved as %s" % (self.target)
            # elif explorer.hasExplorer():
            #     # self.notification.message("Saved as %s" % (targetFilename),
            # lambda : explorer.openExplorer(targetFilename), 4, 'Open folder')
            #     print "Saved as %s" % (self.target)
            # else:
            #     # self.notification.message("Saved as %s" % (targetFilename))
            #     print "Saved as %s" % (self.target)
        self.set_progress_bar_sig.emit(0.0)
        self.finished.emit()
