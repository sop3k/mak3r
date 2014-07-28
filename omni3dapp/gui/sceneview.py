__copyright__ = "Copyright (C) 2013 David Braam - Released under terms of the AGPLv3 License"

import numpy
import math

import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GLU import *
from OpenGL.GL import *

from PySide import QtCore, QtGui, QtOpenGL

from omni3dapp.util import objectscene
from omni3dapp.util import profile
from omni3dapp.gui.util import openglscene
from omni3dapp.util.printerConnection import printerConnectionManager


# from Cura.gui import printWindow
# from Cura.util import profile
# from Cura.util import meshLoader
# from Cura.util import resources
# from Cura.util import sliceEngine
# from Cura.util import pluginInfo
# from Cura.util import removableStorage
# from Cura.util import explorer
# from Cura.gui.util import previewTools
# from Cura.gui.util import openglHelpers
# from Cura.gui.util import engineResultView
# from Cura.gui.tools import youmagineGui
# from Cura.gui.tools import imageToMesh


class SceneView(openglscene.GLScene):
    def __init__(self, parent=None):
        super(SceneView, self).__init__(parent)

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

        # self.openFileButton = openglGui.glButton(self, 4, _("Load"), (0,0), self.showLoadModel)
        # self.printButton = openglGui.glButton(self, 6, _("Print"), (1,0), self.OnPrintButton)
        # self.printButton.setDisabled(True)

        # group = []
        # self.rotateToolButton = openglGui.glRadioButton(self, 8, _("Rotate"), (0,-1), group, self.OnToolSelect)
        # self.scaleToolButton  = openglGui.glRadioButton(self, 9, _("Scale"), (1,-1), group, self.OnToolSelect)
        # self.mirrorToolButton  = openglGui.glRadioButton(self, 10, _("Mirror"), (2,-1), group, self.OnToolSelect)

        # self.resetRotationButton = openglGui.glButton(self, 12, _("Reset"), (0,-2), self.OnRotateReset)
        # self.layFlatButton       = openglGui.glButton(self, 16, _("Lay flat"), (0,-3), self.OnLayFlat)

        # self.resetScaleButton    = openglGui.glButton(self, 13, _("Reset"), (1,-2), self.OnScaleReset)
        # self.scaleMaxButton      = openglGui.glButton(self, 17, _("To max"), (1,-3), self.OnScaleMax)

        # self.mirrorXButton       = openglGui.glButton(self, 14, _("Mirror X"), (2,-2), lambda button: self.OnMirror(0))
        # self.mirrorYButton       = openglGui.glButton(self, 18, _("Mirror Y"), (2,-3), lambda button: self.OnMirror(1))
        # self.mirrorZButton       = openglGui.glButton(self, 22, _("Mirror Z"), (2,-4), lambda button: self.OnMirror(2))

        # self.rotateToolButton.setExpandArrow(True)
        # self.scaleToolButton.setExpandArrow(True)
        # self.mirrorToolButton.setExpandArrow(True)

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

        # self.viewSelection = openglGui.glComboButton(self, _("View mode"), [7,19,11,15,23], [_("Normal"), _("Overhang"), _("Transparent"), _("X-Ray"), _("Layers")], (-1,0), self.OnViewChange)

        # self.youMagineButton = openglGui.glButton(self, 26, _("Share on YouMagine"), (2,0), lambda button: youmagineGui.youmagineManager(self.GetTopLevelParent(), self._scene))
        # self.youMagineButton.setDisabled(True)

        # self.notification = openglGui.glNotification(self, (0, 0))

        # self._engine = sliceEngine.Engine(self._updateEngineProgress)
        # self._engineResultView = engineResultView.engineResultView(self)

        self._sceneUpdateTimer = QtCore.QTimer(self)
        self.connect(timer, QtCore.SIGNAL("timeout()"), self._onRunEngine)
        # self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        # self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)

        # self.OnViewChange()
        # self.OnToolSelect(0)
        # self.updateToolButtons()
        self.updateProfileToControls()

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
        self._init3DView()
        self._viewport = glGetIntegerv(GL_VIEWPORT)
        self._modelMatrix = glGetDoublev(GL_MODELVIEW_MATRIX)
        self._projMatrix = glGetDoublev(GL_PROJECTION_MATRIX)

        # self.object = self.makeObject()

        glClearColor(1,1,1,1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT | GL_STENCIL_BUFFER_BIT)

        glDisable(GL_STENCIL_TEST)
        glDisable(GL_BLEND)
        glEnable(GL_DEPTH_TEST)
        glColorMask(GL_TRUE, GL_TRUE, GL_TRUE, GL_TRUE)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)

    def onPaint(self):
        glTranslated(0.0, 0.0, -self._zoom)
        glRotated(-self._pitch, 1.0, 0.0, 0.0)
        glRotated(self._yaw, 0.0, 0.0, 1.0)
        glTranslated(-self._viewTarget[0], -self._viewTarget[1], -self._viewTarget[2])
        glCallList(self.object)

    def resizeGL(self):
        pass

    def updateGL(self):
        pass

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
        self._sceneUpdateTimer.Start(500, True)
        # self._engine.abortEngine()
        self._scene.updateSizeOffsets()
        self.QueueRefresh()

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
