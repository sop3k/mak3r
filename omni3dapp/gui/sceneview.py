__copyright__ = "Copyright (C) 2013 David Braam - Released under terms of the AGPLv3 License"

import sys
import os
import time
import numpy
import math
import traceback

import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GLU import *
from OpenGL.GL import *

from PySide import QtCore, QtGui
from PySide import QtOpenGL

from omni3dapp.util import objectscene
from omni3dapp.util import profile
from omni3dapp.util import meshLoader
from omni3dapp.util import resources
from omni3dapp.util import version
from omni3dapp.util import sliceEngine
from omni3dapp.util import removableStorage
from omni3dapp.gui.util import openglscene, openglHelpers
from omni3dapp.gui.util import previewTools
from omni3dapp.gui.util import engineResultView
from omni3dapp.util.printerConnection import printerConnectionManager
from omni3dapp.logger import log


# from Cura.gui import printWindow
# from Cura.util import pluginInfo
# from Cura.util import explorer
# from Cura.gui.tools import youmagineGui
# from Cura.gui.tools import imageToMesh


class SceneView(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        super(SceneView, self).__init__(parent)
        
        self._parent = parent
        self._base = self
        self._focus = None
        self._container = openglscene.glGuiContainer(self, (0,0))
        self._shownError = False

        self._context = self.context()
        self._glButtonsTexture = None
        self._glRobotTexture = None
        self._buttonSize = 64

        self._animationList = []
        self.glReleaseList = []
        self._refreshQueued = False
        self._idleCalled = False

        # wx.EVT_ERASE_BACKGROUND(self, self._OnEraseBackground)
        # wx.EVT_LEFT_DOWN(self, self._OnGuiMouseDown)
        # wx.EVT_LEFT_DCLICK(self, self._OnGuiMouseDown)
        # wx.EVT_LEFT_UP(self, self._OnGuiMouseUp)
        # wx.EVT_RIGHT_DOWN(self, self._OnGuiMouseDown)
        # wx.EVT_RIGHT_DCLICK(self, self._OnGuiMouseDown)
        # wx.EVT_RIGHT_UP(self, self._OnGuiMouseUp)
        # wx.EVT_MIDDLE_DOWN(self, self._OnGuiMouseDown)
        # wx.EVT_MIDDLE_DCLICK(self, self._OnGuiMouseDown)
        # wx.EVT_MIDDLE_UP(self, self._OnGuiMouseUp)
        # wx.EVT_MOTION(self, self._OnGuiMouseMotion)
        # wx.EVT_CHAR(self, self._OnGuiKeyChar)
        # wx.EVT_KILL_FOCUS(self, self.OnFocusLost)
        # wx.EVT_IDLE(self, self._OnIdle)

        self._yaw = 30
        self._pitch = 60
        self._zoom = 300
        self._scene = objectscene.Scene()
        self._objectShader = None
        self._objectLoadShader = None
        self._focusObj = None
        self._selectedObj = None
        self._objColors = [None,None,None,None]
        self._mouseX = -1
        self._mouseY = -1
        self._mouseState = None
        self._viewTarget = numpy.array([0,0,0], numpy.float32)
        self._animView = None
        self._animZoom = None
        self._platformMesh = {}
        self._platformTexture = None
        self._isSimpleMode = True
        self._printerConnectionManager = printerConnectionManager.PrinterConnectionManager()

        self._viewport = None
        self._modelMatrix = None
        self._projMatrix = None
        self.tempMatrix = None

        self.openFileButton = openglscene.glButton(self, 4, _("Load"), (0,0), self.showLoadModel)
        self.printButton = openglscene.glButton(self, 6, _("Print"), (1,0), self.OnPrintButton)
        self.printButton.setDisabled(True)

        group = []
        self.rotateToolButton = openglscene.glRadioButton(self, 8, _("Rotate"), (0,-1), group, self.OnToolSelect)
        self.scaleToolButton  = openglscene.glRadioButton(self, 9, _("Scale"), (1,-1), group, self.OnToolSelect)
        self.mirrorToolButton  = openglscene.glRadioButton(self, 10, _("Mirror"), (2,-1), group, self.OnToolSelect)

        self.resetRotationButton = openglscene.glButton(self, 12, _("Reset"), (0,-2), self.OnRotateReset)
        self.layFlatButton       = openglscene.glButton(self, 16, _("Lay flat"), (0,-3), self.OnLayFlat)

        self.resetScaleButton    = openglscene.glButton(self, 13, _("Reset"), (1,-2), self.OnScaleReset)
        self.scaleMaxButton      = openglscene.glButton(self, 17, _("To max"), (1,-3), self.OnScaleMax)

        self.mirrorXButton       = openglscene.glButton(self, 14, _("Mirror X"), (2,-2), lambda button: self.OnMirror(0))
        self.mirrorYButton       = openglscene.glButton(self, 18, _("Mirror Y"), (2,-3), lambda button: self.OnMirror(1))
        self.mirrorZButton       = openglscene.glButton(self, 22, _("Mirror Z"), (2,-4), lambda button: self.OnMirror(2))

        self.rotateToolButton.setExpandArrow(True)
        self.scaleToolButton.setExpandArrow(True)
        self.mirrorToolButton.setExpandArrow(True)

        self.scaleForm = openglscene.glFrame(self, (2, -2))
        openglscene.glGuiLayoutGrid(self.scaleForm)
        openglscene.glLabel(self.scaleForm, _("Scale X"), (0,0))
        self.scaleXctrl = openglscene.glNumberCtrl(self.scaleForm,
                '1.0', (1,0), lambda value: self.OnScaleEntry(value, 0))
        openglscene.glLabel(self.scaleForm, _("Scale Y"), (0,1))
        self.scaleYctrl = openglscene.glNumberCtrl(self.scaleForm,
                '1.0', (1,1), lambda value: self.OnScaleEntry(value, 1))
        openglscene.glLabel(self.scaleForm, _("Scale Z"), (0,2))
        self.scaleZctrl = openglscene.glNumberCtrl(self.scaleForm,
                '1.0', (1,2), lambda value: self.OnScaleEntry(value, 2))
        openglscene.glLabel(self.scaleForm, _("Size X (mm)"), (0,4))
        self.scaleXmmctrl = openglscene.glNumberCtrl(self.scaleForm,
                '0.0', (1,4), lambda value: self.OnScaleEntryMM(value, 0))
        openglscene.glLabel(self.scaleForm, _("Size Y (mm)"), (0,5))
        self.scaleYmmctrl = openglscene.glNumberCtrl(self.scaleForm,
                '0.0', (1,5), lambda value: self.OnScaleEntryMM(value, 1))
        openglscene.glLabel(self.scaleForm, _("Size Z (mm)"), (0,6))
        self.scaleZmmctrl = openglscene.glNumberCtrl(self.scaleForm,
                '0.0', (1,6), lambda value: self.OnScaleEntryMM(value, 2))
        openglscene.glLabel(self.scaleForm, _("Uniform scale"), (0,8))
        self.scaleUniform = openglscene.glCheckbox(self.scaleForm, True,
                (1,8), None)

        self.viewSelection = openglscene.glComboButton(self, _("View mode"),
                [7,19,11,15,23], [_("Normal"), _("Overhang"), _("Transparent"),
                _("X-Ray"), _("Layers")], (-1,0), self.OnViewChange)

        # self.youMagineButton = openglscene.glButton(self, 26, _("Share on YouMagine"), (2,0), lambda button: youmagineGui.youmagineManager(self.GetTopLevelParent(), self._scene))
        # self.youMagineButton.setDisabled(True)

        # self.notification = openglGui.glNotification(self, (0, 0))

        self._engine = sliceEngine.Engine(self._updateEngineProgress)
        self._engineResultView = engineResultView.engineResultView(self)

        self._sceneUpdateTimer = QtCore.QTimer(self)
        self._sceneUpdateTimer.timeout.connect(self._onRunEngine)
        # self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        # self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)

        self.OnViewChange()
        self.OnToolSelect(0)
        self.updateToolButtons()
        self.updateProfileToControls()

    def minimumSizeHint(self):
        return QtCore.QSize(700, 100)

    def _init3DView(self):
        # set viewing projection
        glViewport(0, 0, self.width(), self.height())
        glLoadIdentity()

        glLightfv(GL_LIGHT0, GL_POSITION, [0.2, 0.2, 1.0, 0.0])

        glDisable(GL_RESCALE_NORMAL)
        glDisable(GL_LIGHTING)
        glDisable(GL_LIGHT0)
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glDisable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glClearColor(0.8, 0.8, 0.8, 1.0)
        glClearStencil(0)
        glClearDepth(1.0)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = float(self.width()) / float(self.height())
        gluPerspective(45.0, aspect, 1.0, numpy.max(self._machineSize) * 4)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

    def initializeGL(self):
        self._viewport = glGetIntegerv(GL_VIEWPORT)
        self._modelMatrix = glGetDoublev(GL_MODELVIEW_MATRIX)
        self._projMatrix = glGetDoublev(GL_PROJECTION_MATRIX)

        glClearColor(1,1,1,1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

        glDisable(GL_STENCIL_TEST)
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)

    def paintGL(self):
        self._idleCalled = False
        h = self.height()
        w = self.width()
        oldButtonSize = self._buttonSize
        if h / 3 < w / 4:
            w = h * 4 / 3
        if w < 64 * 8:
            self._buttonSize = 32
        elif w < 64 * 10:
            self._buttonSize = 48
        elif w < 64 * 15:
            self._buttonSize = 64
        elif w < 64 * 20:
            self._buttonSize = 80
        else:
            self._buttonSize = 96
        if self._buttonSize != oldButtonSize:
            self._container.updateLayout()

        try:
            self._context.makeCurrent()
            for obj in self.glReleaseList:
                obj.release()
            # del self.glReleaseList
            renderStartTime = time.time()
            self.onPaint()
            self._drawScene()
            glFlush()
            if version.isDevVersion():
                renderTime = time.time() - renderStartTime
                if renderTime == 0:
                    renderTime = 0.001
                glLoadIdentity()
                glTranslated(10.0, self.height() - 30.0, -1.0)
                glColor4f(0.2,0.2,0.2,0.5)
                openglHelpers.glDrawStringLeft("fps:%d" % (1 / renderTime))
        except:
            # When an exception happens, catch it and show a message box. If the exception is not caught the draw function bugs out.
            # Only show this exception once so we do not overload the user with popups.
            errStr = _("An error has occurred during the 3D view drawing.")
            tb = traceback.extract_tb(sys.exc_info()[2])
            errStr += "\n%s: '%s'" % (str(sys.exc_info()[0].__name__), str(sys.exc_info()[1]))
            log.error(errStr)
            for n in xrange(len(tb)-1, -1, -1):
                locationInfo = tb[n]
                errStr += "\n @ %s:%s:%d" % (os.path.basename(locationInfo[0]), locationInfo[2], locationInfo[1])
            if not self._shownError:
                traceback.print_exc()
                log.error(errStr)
                # TODO: show modal box with error message
                # wx.CallAfter(wx.MessageBox, errStr, _("3D window error"), wx.OK | wx.ICON_EXCLAMATION)
                self._shownError = True

    def resizeGL(self, width, height):
        self._container.setSize(0, 0, width, height)
        self._container.updateLayout()
        # glViewport(0, 0, width, height)
        # glLoadIdentity()

    def _drawScene(self):
        if self._glButtonsTexture is None:
            self._glButtonsTexture = self.loadGLTexture('glButtons.png')
            self._glRobotTexture = self.loadGLTexture('UltimakerRobot.png')

        glDisable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_LIGHTING)
        glColor4ub(255,255,255,255)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, self.width()-1, self.height()-1, 0, -1000.0, 1000.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        self._container.draw()

    def onPaint(self):
        connectionGroup = self._printerConnectionManager.getAvailableGroup()
        if len(removableStorage.getPossibleSDcardDrives()) > 0 and (connectionGroup is None or connectionGroup.getPriority() < 0):
          self.printButton._imageID = 2
          self.printButton._tooltip = _("Toolpath to SD")
        elif connectionGroup is not None:
          self.printButton._imageID = connectionGroup.getIconID()
          self.printButton._tooltip = _("Print with %s") % (connectionGroup.getName())
        else:
          self.printButton._imageID = 3
          self.printButton._tooltip = _("Save toolpath")

        if self._animView is not None:
            self._viewTarget = self._animView.getPosition()
            if self._animView.isDone():
                self._animView = None
        if self._animZoom is not None:
            self._zoom = self._animZoom.getPosition()
            if self._animZoom.isDone():
                self._animZoom = None
        if self._objectShader is None: #TODO: add loading shaders from file(s)
            if openglHelpers.hasShaderSupport():
                self._objectShader = openglHelpers.GLShader("""
                    varying float light_amount;

                    void main(void)
                    {
                        gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
                        gl_FrontColor = gl_Color;

                        light_amount = abs(dot(normalize(gl_NormalMatrix * gl_Normal), normalize(gl_LightSource[0].position.xyz)));
                        light_amount += 0.2;
                    }
                                    ""","""
                    varying float light_amount;

                    void main(void)
                    {
                        gl_FragColor = vec4(gl_Color.xyz * light_amount, gl_Color[3]);
                    }
                """)
                self._objectOverhangShader = openglHelpers.GLShader("""
                    uniform float cosAngle;
                    uniform mat3 rotMatrix;
                    varying float light_amount;

                    void main(void)
                    {
                        gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
                        gl_FrontColor = gl_Color;

                        light_amount = abs(dot(normalize(gl_NormalMatrix * gl_Normal), normalize(gl_LightSource[0].position.xyz)));
                        light_amount += 0.2;
                        if (normalize(rotMatrix * gl_Normal).z < -cosAngle)
                        {
                            light_amount = -10.0;
                        }
                    }
                ""","""
                    varying float light_amount;

                    void main(void)
                    {
                        if (light_amount == -10.0)
                        {
                            gl_FragColor = vec4(1.0, 0.0, 0.0, gl_Color[3]);
                        }else{
                            gl_FragColor = vec4(gl_Color.xyz * light_amount, gl_Color[3]);
                        }
                    }
                                    """)
                self._objectLoadShader = openglHelpers.GLShader("""
                    uniform float intensity;
                    uniform float scale;
                    varying float light_amount;

                    void main(void)
                    {
                        vec4 tmp = gl_Vertex;
                        tmp.x += sin(tmp.z/5.0+intensity*30.0) * scale * intensity;
                        tmp.y += sin(tmp.z/3.0+intensity*40.0) * scale * intensity;
                        gl_Position = gl_ModelViewProjectionMatrix * tmp;
                        gl_FrontColor = gl_Color;

                        light_amount = abs(dot(normalize(gl_NormalMatrix * gl_Normal), normalize(gl_LightSource[0].position.xyz)));
                        light_amount += 0.2;
                    }
            ""","""
                uniform float intensity;
                varying float light_amount;

                void main(void)
                {
                    gl_FragColor = vec4(gl_Color.xyz * light_amount, 1.0-intensity);
                }
                """)
            if self._objectShader is None or not self._objectShader.isValid(): #Could not make shader.
                self._objectShader = openglHelpers.GLFakeShader()
                self._objectOverhangShader = openglHelpers.GLFakeShader()
                self._objectLoadShader = None
        self._init3DView()
        glTranslate(0.0, 0.0, -self._zoom)
        glRotate(-self._pitch, 1.0, 0.0, 0.0)
        glRotate(self._yaw, 0.0, 0.0, 1.0)
        glTranslate(-self._viewTarget[0], -self._viewTarget[1], -self._viewTarget[2])

        self._viewport = glGetIntegerv(GL_VIEWPORT)
        self._modelMatrix = glGetDoublev(GL_MODELVIEW_MATRIX)
        self._projMatrix = glGetDoublev(GL_PROJECTION_MATRIX)

        glClearColor(1,1,1,1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

        if self.viewMode != 'gcode':
            for n in xrange(0, len(self._scene.objects())):
                obj = self._scene.objects()[n]
                glColor4ub((n >> 16) & 0xFF, (n >> 8) & 0xFF, (n >> 0) & 0xFF, 0xFF)
                self._renderObject(obj)

        if self._mouseX > -1: # mouse has not passed over the opengl window.
            glFlush()
            n = glReadPixels(self._mouseX, self.height() - 1 - self._mouseY, 1, 1, GL_RGBA, GL_UNSIGNED_INT_8_8_8_8)[0][0] >> 8
            if n < len(self._scene.objects()):
                self._focusObj = self._scene.objects()[n]
            else:
                self._focusObj = None
            f = glReadPixels(self._mouseX, self.height() - 1 - self._mouseY, 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)[0][0]
            #self.GetTopLevelParent().SetTitle(hex(n) + " " + str(f))
            self._mouse3Dpos = openglHelpers.unproject(self._mouseX, self._viewport[1] + self._viewport[3] - self._mouseY, f, self._modelMatrix, self._projMatrix, self._viewport)
            self._mouse3Dpos -= self._viewTarget

        self._init3DView()
        glTranslate(0,0,-self._zoom)
        glRotate(-self._pitch, 1,0,0)
        glRotate(self._yaw, 0,0,1)
        glTranslate(-self._viewTarget[0],-self._viewTarget[1],-self._viewTarget[2])

        self._objectShader.unbind()
        self._engineResultView.OnDraw()
        if self.viewMode != 'gcode':
            glStencilFunc(GL_ALWAYS, 1, 1)
            glStencilOp(GL_INCR, GL_INCR, GL_INCR)

            if self.viewMode == 'overhang':
                self._objectOverhangShader.bind()
                self._objectOverhangShader.setUniform('cosAngle', math.cos(math.radians(90 - profile.getProfileSettingFloat('support_angle'))))
            else:
                self._objectShader.bind()
            for obj in self._scene.objects():
                if obj._loadAnim is not None:
                    if obj._loadAnim.isDone():
                        obj._loadAnim = None
                    else:
                        continue
                brightness = 1.0
                if self._focusObj == obj:
                    brightness = 1.2
                elif self._focusObj is not None or self._selectedObj is not None and obj != self._selectedObj:
                    brightness = 0.8

                if self._selectedObj == obj or self._selectedObj is None:
                    #If we want transparent, then first render a solid black model to remove the printer size lines.
                    if self.viewMode == 'transparent':
                        glColor4f(0, 0, 0, 0)
                        self._renderObject(obj)
                        glEnable(GL_BLEND)
                        glBlendFunc(GL_ONE, GL_ONE)
                        glDisable(GL_DEPTH_TEST)
                        brightness *= 0.5
                    if self.viewMode == 'xray':
                        glColorMask(GL_FALSE, GL_FALSE, GL_FALSE, GL_FALSE)
                    glStencilOp(GL_INCR, GL_INCR, GL_INCR)
                    glEnable(GL_STENCIL_TEST)

                if self.viewMode == 'overhang':
                    if self._selectedObj == obj and self.tempMatrix is not None:
                        self._objectOverhangShader.setUniform('rotMatrix', obj.getMatrix() * self.tempMatrix)
                    else:
                        self._objectOverhangShader.setUniform('rotMatrix', obj.getMatrix())

                if not self._scene.checkPlatform(obj):
                    glColor4f(0.5 * brightness, 0.5 * brightness, 0.5 * brightness, 0.8 * brightness)
                    self._renderObject(obj)
                else:
                    self._renderObject(obj, brightness)
                glDisable(GL_STENCIL_TEST)
                glDisable(GL_BLEND)
                glEnable(GL_DEPTH_TEST)
                glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)

            if self.viewMode == 'xray':
                glPushMatrix()
                glLoadIdentity()
                glEnable(GL_STENCIL_TEST)
                glStencilOp(GL_KEEP, GL_KEEP, GL_KEEP) #Keep values
                glDisable(GL_DEPTH_TEST)
                for i in xrange(2, 15, 2): #All even values
                    glStencilFunc(GL_EQUAL, i, 0xFF)
                    glColor(float(i)/10, float(i)/10, float(i)/5)
                    glBegin(GL_QUADS)
                    glVertex3f(-1000,-1000,-10)
                    glVertex3f( 1000,-1000,-10)
                    glVertex3f( 1000, 1000,-10)
                    glVertex3f(-1000, 1000,-10)
                    glEnd()
                for i in xrange(1, 15, 2): #All odd values
                    glStencilFunc(GL_EQUAL, i, 0xFF)
                    glColor(float(i)/10, 0, 0)
                    glBegin(GL_QUADS)
                    glVertex3f(-1000,-1000,-10)
                    glVertex3f( 1000,-1000,-10)
                    glVertex3f( 1000, 1000,-10)
                    glVertex3f(-1000, 1000,-10)
                    glEnd()
                glPopMatrix()
                glDisable(GL_STENCIL_TEST)
                glEnable(GL_DEPTH_TEST)

            self._objectShader.unbind()

            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glEnable(GL_BLEND)
            if self._objectLoadShader is not None:
                self._objectLoadShader.bind()
                glColor4f(0.2, 0.6, 1.0, 1.0)
                for obj in self._scene.objects():
                    if obj._loadAnim is None:
                        continue
                    self._objectLoadShader.setUniform('intensity', obj._loadAnim.getPosition())
                    self._objectLoadShader.setUniform('scale', obj.getBoundaryCircle() / 10)
                    self._renderObject(obj)
                self._objectLoadShader.unbind()
                glDisable(GL_BLEND)

        self._drawMachine()

        if self.viewMode != 'gcode':
            #Draw the object box-shadow, so you can see where it will collide with other objects.
            if self._selectedObj is not None:
                glEnable(GL_BLEND)
                glEnable(GL_CULL_FACE)
                glColor4f(0,0,0,0.16)
                glDepthMask(False)
                for obj in self._scene.objects():
                    glPushMatrix()
                    glTranslatef(obj.getPosition()[0], obj.getPosition()[1], 0)
                    glBegin(GL_TRIANGLE_FAN)
                    for p in obj._boundaryHull[::-1]:
                        glVertex3f(p[0], p[1], 0)
                    glEnd()
                    glPopMatrix()
                if self._scene.isOneAtATime(): #Check print sequence mode.
                    glPushMatrix()
                    glColor4f(0,0,0,0.06)
                    glTranslatef(self._selectedObj.getPosition()[0], self._selectedObj.getPosition()[1], 0)
                    glBegin(GL_TRIANGLE_FAN)
                    for p in self._selectedObj._printAreaHull[::-1]:
                        glVertex3f(p[0], p[1], 0)
                    glEnd()
                    glBegin(GL_TRIANGLE_FAN)
                    for p in self._selectedObj._headAreaMinHull[::-1]:
                        glVertex3f(p[0], p[1], 0)
                    glEnd()
                    glPopMatrix()
                glDepthMask(True)
                glDisable(GL_CULL_FACE)

            #Draw the outline of the selected object on top of everything else except the GUI.
            if self._selectedObj is not None and self._selectedObj._loadAnim is None:
                glDisable(GL_DEPTH_TEST)
                glEnable(GL_CULL_FACE)
                glEnable(GL_STENCIL_TEST)
                glDisable(GL_BLEND)
                glStencilFunc(GL_EQUAL, 0, 255)

                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
                glLineWidth(2)
                glColor4f(1,1,1,0.5)
                self._renderObject(self._selectedObj)
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

                glViewport(0, 0, self.GetSize().GetWidth(), self.GetSize().GetHeight())
                glDisable(GL_STENCIL_TEST)
                glDisable(GL_CULL_FACE)
                glEnable(GL_DEPTH_TEST)

            if self._selectedObj is not None:
                glPushMatrix()
                pos = self.getObjectCenterPos()
                glTranslate(pos[0], pos[1], pos[2])
                self.tool.OnDraw()
                glPopMatrix()
        if self.viewMode == 'overhang' and not openglHelpers.hasShaderSupport():
            glDisable(GL_DEPTH_TEST)
            glPushMatrix()
            glLoadIdentity()
            glTranslate(0,-4,-10)
            glColor4ub(60,60,60,255)
            openglHelpers.glDrawStringCenter(_("Overhang view not working due to lack of OpenGL shaders support."))
            glPopMatrix()

    def _renderObject(self, obj, brightness=0, addSink=True):
        glPushMatrix()
        if addSink:
            glTranslate(obj.getPosition()[0], obj.getPosition()[1], obj.getSize()[2] / 2 - profile.getProfileSettingFloat('object_sink'))
        else:
            glTranslate(obj.getPosition()[0], obj.getPosition()[1], obj.getSize()[2] / 2)

        if self.tempMatrix is not None and obj == self._selectedObj:
            glMultMatrixf(openglHelpers.convert3x3MatrixTo4x4(self.tempMatrix))

        offset = obj.getDrawOffset()
        glTranslate(-offset[0], -offset[1], -offset[2] - obj.getSize()[2] / 2)

        glMultMatrixf(openglHelpers.convert3x3MatrixTo4x4(obj.getMatrix()))

        n = 0
        for m in obj._meshList:
            if m.vbo is None:
                m.vbo = openglHelpers.GLVBO(GL_TRIANGLES, m.vertexes, m.normal)
            if brightness != 0:
                glColor4fv(map(lambda idx: idx * brightness, self._objColors[n]))
                n += 1
            m.vbo.render()
        glPopMatrix()

    def _drawMachine(self):
        glEnable(GL_CULL_FACE)
        glEnable(GL_BLEND)

        size = [profile.getMachineSettingFloat('machine_width'),
                profile.getMachineSettingFloat('machine_depth'),
                profile.getMachineSettingFloat('machine_height')]

        machine = profile.getMachineSetting('machine_type')
        if machine.startswith('ultimaker'):
            if machine not in self._platformMesh:
                meshes = meshLoader.loadMeshes(resources.getPathForMesh(machine + '_platform.stl'))
                if len(meshes) > 0:
                    self._platformMesh[machine] = meshes[0]
                else:
                    self._platformMesh[machine] = None
                if machine == 'ultimaker2':
                    self._platformMesh[machine]._drawOffset = numpy.array([0,-37,145], numpy.float32)
                else:
                    self._platformMesh[machine]._drawOffset = numpy.array([0,0,2.5], numpy.float32)
            glColor4f(1,1,1,0.5)
            self._objectShader.bind()
            self._renderObject(self._platformMesh[machine], False, False)
            self._objectShader.unbind()

            #For the Ultimaker 2 render the texture on the back plate to show the Ultimaker2 text.
            if machine == 'ultimaker2':
                if not hasattr(self._platformMesh[machine], 'texture'):
                    self._platformMesh[machine].texture = self.loadGLTexture('Ultimaker2backplate.png')
                glBindTexture(GL_TEXTURE_2D, self._platformMesh[machine].texture)
                glEnable(GL_TEXTURE_2D)
                glPushMatrix()
                glColor4f(1,1,1,1)

                glTranslate(0,150,-5)
                h = 50
                d = 8
                w = 100
                glEnable(GL_BLEND)
                glBlendFunc(GL_DST_COLOR, GL_ZERO)
                glBegin(GL_QUADS)
                glTexCoord2f(1, 0)
                glVertex3f( w, 0, h)
                glTexCoord2f(0, 0)
                glVertex3f(-w, 0, h)
                glTexCoord2f(0, 1)
                glVertex3f(-w, 0, 0)
                glTexCoord2f(1, 1)
                glVertex3f( w, 0, 0)

                glTexCoord2f(1, 0)
                glVertex3f(-w, d, h)
                glTexCoord2f(0, 0)
                glVertex3f( w, d, h)
                glTexCoord2f(0, 1)
                glVertex3f( w, d, 0)
                glTexCoord2f(1, 1)
                glVertex3f(-w, d, 0)
                glEnd()
                glDisable(GL_TEXTURE_2D)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                glPopMatrix()
        else:
            glColor4f(0,0,0,1)
            glLineWidth(3)
            glBegin(GL_LINES)
            glVertex3f(-size[0] / 2, -size[1] / 2, 0)
            glVertex3f(-size[0] / 2, -size[1] / 2, 10)
            glVertex3f(-size[0] / 2, -size[1] / 2, 0)
            glVertex3f(-size[0] / 2+10, -size[1] / 2, 0)
            glVertex3f(-size[0] / 2, -size[1] / 2, 0)
            glVertex3f(-size[0] / 2, -size[1] / 2+10, 0)
            glEnd()

        glDepthMask(False)

        polys = profile.getMachineSizePolygons()
        height = profile.getMachineSettingFloat('machine_height')
        circular = profile.getMachineSetting('machine_shape') == 'Circular'
        glBegin(GL_QUADS)
        # Draw the sides of the build volume.
        for n in xrange(0, len(polys[0])):
            if not circular:
                if n % 2 == 0:
                    glColor4ub(5, 171, 231, 96)
                else:
                    glColor4ub(5, 171, 231, 64)
            else:
                glColor4ub(5, 171, 231, 96)

            glVertex3f(polys[0][n][0], polys[0][n][1], height)
            glVertex3f(polys[0][n][0], polys[0][n][1], 0)
            glVertex3f(polys[0][n-1][0], polys[0][n-1][1], 0)
            glVertex3f(polys[0][n-1][0], polys[0][n-1][1], height)
        glEnd()

        #Draw top of build volume.
        glColor4ub(5, 171, 231, 128)
        glBegin(GL_TRIANGLE_FAN)
        for p in polys[0][::-1]:
            glVertex3f(p[0], p[1], height)
        glEnd()

        #Draw checkerboard
        if self._platformTexture is None:
            self._platformTexture = self.loadGLTexture('checkerboard.png')
            glBindTexture(GL_TEXTURE_2D, self._platformTexture)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glColor4f(1,1,1,0.5)
        glBindTexture(GL_TEXTURE_2D, self._platformTexture)
        glEnable(GL_TEXTURE_2D)
        glBegin(GL_TRIANGLE_FAN)
        for p in polys[0]:
            glTexCoord2f(p[0]/20, p[1]/20)
            glVertex3f(p[0], p[1], 0)
        glEnd()

        #Draw no-go zones. (clips in case of UM2)
        glDisable(GL_TEXTURE_2D)
        glColor4ub(127, 127, 127, 200)
        for poly in polys[1:]:
            glBegin(GL_TRIANGLE_FAN)
            for p in poly:
                glTexCoord2f(p[0]/20, p[1]/20)
                glVertex3f(p[0], p[1], 0)
            glEnd()

        glDepthMask(True)
        glDisable(GL_BLEND)
        glDisable(GL_CULL_FACE)

    def add(self, ctrl):
        if hasattr(self, '_container'):
            self._container.add(ctrl)

    def updateProfileToControls(self):
        oldSimpleMode = self._isSimpleMode
        self._isSimpleMode = profile.getPreference('startMode') == 'Simple'
        if self._isSimpleMode != oldSimpleMode:
            self._scene.arrangeAll()
            self.sceneUpdated()
        self._scene.updateSizeOffsets(True)
        self._machineSize = numpy.array([
            profile.getMachineSettingFloat('machine_width'),
            profile.getMachineSettingFloat('machine_depth'),
            profile.getMachineSettingFloat('machine_height')])
        self._objColors[0] = profile.getPreferenceColour('model_colour')
        self._objColors[1] = profile.getPreferenceColour('model_colour2')
        self._objColors[2] = profile.getPreferenceColour('model_colour3')
        self._objColors[3] = profile.getPreferenceColour('model_colour4')
        self._scene.updateMachineDimensions()
        self.updateModelSettingsToControls()

    def sceneUpdated(self):
        self._sceneUpdateTimer.start(500)
        self._engine.abortEngine()
        self._scene.updateSizeOffsets()
        self.queueRefresh()

    def queueRefresh(self):
        if self._idleCalled:
            # wx.CallAfter(self.Refresh)
            self.updateGL()
        else:
            self._refreshQueued = True

    def updateModelSettingsToControls(self):
        if self._selectedObj is not None:
            scale = self._selectedObj.getScale()
            size = self._selectedObj.getSize()
            self.scaleXctrl.setValue(round(scale[0], 2))
            self.scaleYctrl.setValue(round(scale[1], 2))
            self.scaleZctrl.setValue(round(scale[2], 2))
            self.scaleXmmctrl.setValue(round(size[0], 2))
            self.scaleYmmctrl.setValue(round(size[1], 2))
            self.scaleZmmctrl.setValue(round(size[2], 2))

    def _onRunEngine(self, *args, **kwargs):
        if self._isSimpleMode:
            self._parent.setupSlice()
        self._engine.runEngine(self._scene)
        if self._isSimpleMode:
            profile.resetTempOverride()

    def OnViewChange(self):
        if self.viewSelection.getValue() == 4:
            self.viewMode = 'gcode'
            self.tool = previewTools.toolNone(self)
        elif self.viewSelection.getValue() == 1:
            self.viewMode = 'overhang'
        elif self.viewSelection.getValue() == 2:
            self.viewMode = 'transparent'
        elif self.viewSelection.getValue() == 3:
            self.viewMode = 'xray'
        else:
            self.viewMode = 'normal'
        self._engineResultView.setEnabled(self.viewMode == 'gcode')
        self.queueRefresh()

    def OnToolSelect(self, button):
        if self.rotateToolButton.getSelected():
            self.tool = previewTools.toolRotate(self)
        elif self.scaleToolButton.getSelected():
            self.tool = previewTools.toolScale(self)
        elif self.mirrorToolButton.getSelected():
            self.tool = previewTools.toolNone(self)
        else:
            self.tool = previewTools.toolNone(self)
        self.resetRotationButton.setHidden(not self.rotateToolButton.getSelected())
        self.layFlatButton.setHidden(not self.rotateToolButton.getSelected())
        self.resetScaleButton.setHidden(not self.scaleToolButton.getSelected())
        self.scaleMaxButton.setHidden(not self.scaleToolButton.getSelected())
        self.scaleForm.setHidden(not self.scaleToolButton.getSelected())
        self.mirrorXButton.setHidden(not self.mirrorToolButton.getSelected())
        self.mirrorYButton.setHidden(not self.mirrorToolButton.getSelected())
        self.mirrorZButton.setHidden(not self.mirrorToolButton.getSelected())

    def updateToolButtons(self):
        if self._selectedObj is None:
            hidden = True
        else:
            hidden = False
        self.rotateToolButton.setHidden(hidden)
        self.scaleToolButton.setHidden(hidden)
        self.mirrorToolButton.setHidden(hidden)
        if hidden:
            self.rotateToolButton.setSelected(False)
            self.scaleToolButton.setSelected(False)
            self.mirrorToolButton.setSelected(False)
            self.OnToolSelect(0)

    def _updateEngineProgress(self, progressValue):
        result = self._engine.getResult()
        finished = result is not None and result.isFinished()
        if not finished:
            if self.printButton.getProgressBar() is not None and progressValue >= 0.0 and abs(self.printButton.getProgressBar() - progressValue) < 0.01:
                return
        self.printButton.setDisabled(not finished)
        if progressValue >= 0.0:
            self.printButton.setProgressBar(progressValue)
        else:
            self.printButton.setProgressBar(None)
        self._engineResultView.setResult(result)
        if finished:
            self.printButton.setProgressBar(None)
            text = '%s' % (result.getPrintTime())
            for e in xrange(0, int(profile.getMachineSetting('extruder_amount'))):
                amount = result.getFilamentAmount(e)
                if amount is None:
                    continue
                text += '\n%s' % (amount)
                cost = result.getFilamentCost(e)
                if cost is not None:
                    text += '\n%s' % (cost)
            self.printButton.setBottomText(text)
        else:
            self.printButton.setBottomText('')
        self.queueRefresh()

    def OnRotateReset(self, button):
        if self._selectedObj is None:
            return
        self._selectedObj.resetRotation()
        self._scene.pushFree(self._selectedObj)
        self._selectObject(self._selectedObj)
        self.sceneUpdated()

    def OnLayFlat(self, button):
        if self._selectedObj is None:
            return
        self._selectedObj.layFlat()
        self._scene.pushFree(self._selectedObj)
        self._selectObject(self._selectedObj)
        self.sceneUpdated()

    def OnScaleReset(self, button):
        if self._selectedObj is None:
            return
        self._selectedObj.resetScale()
        self._selectObject(self._selectedObj)
        self.updateProfileToControls()
        self.sceneUpdated()

    def OnScaleMax(self, button):
        if self._selectedObj is None:
            return
        machine = profile.getMachineSetting('machine_type')
        self._selectedObj.setPosition(numpy.array([0.0, 0.0]))
        self._scene.pushFree(self._selectedObj)
        #self.sceneUpdated()
        if machine == "ultimaker2":
            #This is bad and Jaime should feel bad!
            self._selectedObj.setPosition(numpy.array([0.0,-10.0]))
            self._selectedObj.scaleUpTo(self._machineSize - numpy.array(profile.calculateObjectSizeOffsets() + [0.0], numpy.float32) * 2 - numpy.array([3,3,3], numpy.float32))
            self._selectedObj.setPosition(numpy.array([0.0,0.0]))
            self._scene.pushFree(self._selectedObj)
        else:
            self._selectedObj.setPosition(numpy.array([0.0, 0.0]))
            self._scene.pushFree(self._selectedObj)
            self._selectedObj.scaleUpTo(self._machineSize - numpy.array(profile.calculateObjectSizeOffsets() + [0.0], numpy.float32) * 2 - numpy.array([3,3,3], numpy.float32))
        self._scene.pushFree(self._selectedObj)
        self._selectObject(self._selectedObj)
        self.updateProfileToControls()
        self.sceneUpdated()

    def OnMirror(self, axis):
        if self._selectedObj is None:
            return
        self._selectedObj.mirror(axis)
        self.sceneUpdated()

    def OnPrintButton(self, button):
        print "Entered OnPrintButton method"
        # if button == 1:
        #     connectionGroup = self._printerConnectionManager.getAvailableGroup()
        #     if len(removableStorage.getPossibleSDcardDrives()) > 0 and (connectionGroup is None or connectionGroup.getPriority() < 0):
        #         drives = removableStorage.getPossibleSDcardDrives()
        #         if len(drives) > 1:
        #             dlg = wx.SingleChoiceDialog(self, "Select SD drive", "Multiple removable drives have been found,\nplease select your SD card drive", map(lambda n: n[0], drives))
        #             if dlg.ShowModal() != wx.ID_OK:
        #                 dlg.Destroy()
        #                 return
        #             drive = drives[dlg.GetSelection()]
        #             dlg.Destroy()
        #         else:
        #             drive = drives[0]
        #         filename = self._scene._objectList[0].getName() + profile.getGCodeExtension()
        #         threading.Thread(target=self._saveGCode,args=(drive[1] + filename, drive[1])).start()
        #     elif connectionGroup is not None:
        #         connections = connectionGroup.getAvailableConnections()
        #         if len(connections) < 2:
        #             connection = connections[0]
        #         else:
        #             dlg = wx.SingleChoiceDialog(self, "Select the %s connection to use" % (connectionGroup.getName()), "Multiple %s connections found" % (connectionGroup.getName()), map(lambda n: n.getName(), connections))
        #             if dlg.ShowModal() != wx.ID_OK:
        #                 dlg.Destroy()
        #                 return
        #             connection = connections[dlg.GetSelection()]
        #             dlg.Destroy()
        #         self._openPrintWindowForConnection(connection)
        #     else:
        #         self.showSaveGCode()
        # if button == 3:
        #     menu = wx.Menu()
        #     connections = self._printerConnectionManager.getAvailableConnections()
        #     menu.connectionMap = {}
        #     for connection in connections:
        #         i = menu.Append(-1, _("Print with %s") % (connection.getName()))
        #         menu.connectionMap[i.GetId()] = connection
        #         self.Bind(wx.EVT_MENU, lambda e: self._openPrintWindowForConnection(e.GetEventObject().connectionMap[e.GetId()]), i)
        #     self.Bind(wx.EVT_MENU, lambda e: self.showSaveGCode(), menu.Append(-1, _("Save GCode...")))
        #     self.Bind(wx.EVT_MENU, lambda e: self._showEngineLog(), menu.Append(-1, _("Slice engine log...")))
        #     self.PopupMenu(menu)
        #     menu.Destroy()

    def showLoadModel(self, button = 1):
        print "Entered showLoadModel method"
        # if button == 1:
        #     dlg=wx.FileDialog(self, _("Open 3D model"), os.path.split(profile.getPreference('lastFile'))[0], style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST|wx.FD_MULTIPLE)

        #     wildcardList = ';'.join(map(lambda s: '*' + s, meshLoader.loadSupportedExtensions() + imageToMesh.supportedExtensions() + ['.g', '.gcode']))
        #     wildcardFilter = "All (%s)|%s;%s" % (wildcardList, wildcardList, wildcardList.upper())
        #     wildcardList = ';'.join(map(lambda s: '*' + s, meshLoader.loadSupportedExtensions()))
        #     wildcardFilter += "|Mesh files (%s)|%s;%s" % (wildcardList, wildcardList, wildcardList.upper())
        #     wildcardList = ';'.join(map(lambda s: '*' + s, imageToMesh.supportedExtensions()))
        #     wildcardFilter += "|Image files (%s)|%s;%s" % (wildcardList, wildcardList, wildcardList.upper())
        #     wildcardList = ';'.join(map(lambda s: '*' + s, ['.g', '.gcode']))
        #     wildcardFilter += "|GCode files (%s)|%s;%s" % (wildcardList, wildcardList, wildcardList.upper())

        #     dlg.SetWildcard(wildcardFilter)
        #     if dlg.ShowModal() != wx.ID_OK:
        #         dlg.Destroy()
        #         return
        #     filenames = dlg.GetPaths()
        #     dlg.Destroy()
        #     if len(filenames) < 1:
        #         return False
        #     profile.putPreference('lastFile', filenames[0])
        #     self.loadFiles(filenames)

    def loadGLTexture(self, filename):
        filepath = resources.getPathForImage(filename)
        return self.bindTexture(QtGui.QPixmap(filepath))
