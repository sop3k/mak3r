from __future__ import division
__copyright__ = "Copyright (C) 2013 David Braam - Released under terms of the AGPLv3 License"

import os
import time

import OpenGL
OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *

from PySide import QtCore, QtGui

from omni3dapp.util import version
from omni3dapp.gui.util import openglHelpers

class animation(object):
    def __init__(self, gui, start, end, runTime):
        self._start = start
        self._end = end
        self._startTime = time.time()
        self._runTime = runTime
        gui._animationList.append(self)

    def isDone(self):
        return time.time() > self._startTime + self._runTime

    def getPosition(self):
        if self.isDone():
            return self._end
        f = (time.time() - self._startTime) / self._runTime
        ts = f*f
        tc = f*f*f
        #f = 6*tc*ts + -15*ts*ts + 10*tc
        f = tc + -3*ts + 3*f
        return self._start + (self._end - self._start) * f

class glGuiControl(object):
    def __init__(self, parent, pos):
        self._parent = parent
        self._base = parent._base
        self._pos = pos
        self._size = (0, 0, 1, 1)
        self._parent.add(self)

    def setSize(self, x, y, w, h):
        self._size = (x, y, w, h)

    def getSize(self):
        return self._size

    def getMinSize(self):
        return 1, 1

    def updateLayout(self):
        pass

    def focusNext(self):
        for n in xrange(self._parent._glGuiControlList.index(self) + 1, len(self._parent._glGuiControlList)):
            if self._parent._glGuiControlList[n].setFocus():
                return
        for n in xrange(0, self._parent._glGuiControlList.index(self)):
            if self._parent._glGuiControlList[n].setFocus():
                return

    def focusPrevious(self):
        for n in xrange(self._parent._glGuiControlList.index(self) -1, -1, -1):
            if self._parent._glGuiControlList[n].setFocus():
                return
        for n in xrange(len(self._parent._glGuiControlList) - 1, self._parent._glGuiControlList.index(self), -1):
            if self._parent._glGuiControlList[n].setFocus():
                return

    def setFocus(self):
        return False

    def hasFocus(self):
        return self._base._focus == self

    def onMouseReleaseEvent(self, x, y):
        pass

    def onKeyChar(self, key):
        pass


class glGuiContainer(glGuiControl):
    def __init__(self, parent, pos):
        self._glGuiControlList = []
        glGuiLayoutButtons(self)
        super(glGuiContainer, self).__init__(parent, pos)

    def add(self, ctrl):
        self._glGuiControlList.append(ctrl)
        self.updateLayout()

    def onMousePressEvent(self, x, y, button):
        for ctrl in self._glGuiControlList:
            if ctrl.onMousePressEvent(x, y, button):
                return True
        return False

    def onMouseReleaseEvent(self, x, y):
        for ctrl in self._glGuiControlList:
            if ctrl.onMouseReleaseEvent(x, y):
                return True
        return False

    def onMouseMoveEvent(self, x, y):
        handled = False
        for ctrl in self._glGuiControlList:
            if ctrl.onMouseMoveEvent(x, y):
                handled = True
        return handled

    def draw(self, painter=None):
        for ctrl in self._glGuiControlList:
            ctrl.draw(painter)

    def updateLayout(self):
        self._layout.update()
        for ctrl in self._glGuiControlList:
            ctrl.updateLayout()


class glGuiLayoutButtons(object):
    def __init__(self, parent):
        self._parent = parent
        self._parent._layout = self

    def update(self):
        bs = self._parent._base._buttonSize
        x0, y0, w, h = self._parent.getSize()
        gridSize = bs * 1.0
        for ctrl in self._parent._glGuiControlList:
            pos = ctrl._pos
            if pos[0] < 0:
                x = w + pos[0] * gridSize - bs * 0.2
            else:
                x = pos[0] * gridSize + bs * 0.2
            if pos[1] < 0:
                y = h + pos[1] * gridSize * 1.2 - bs * 0.0
            else:
                y = pos[1] * gridSize * 1.2 + bs * 0.2
            ctrl.setSize(x, y, gridSize, gridSize)

    def getLayoutSize(self):
        _, _, w, h = self._parent.getSize()
        return w, h


class glGuiLayoutGrid(object):
    def __init__(self, parent):
        self._parent = parent
        self._parent._layout = self
        self._size = 0,0
        self._alignBottom = True

    def update(self):
        borderSize = self._parent._base._buttonSize * 0.2
        x0, y0, w, h = self._parent.getSize()
        x0 += borderSize
        y0 += borderSize
        widths = {}
        heights = {}
        for ctrl in self._parent._glGuiControlList:
            x, y = ctrl._pos
            w, h = ctrl.getMinSize()
            if not x in widths:
                widths[x] = w
            else:
                widths[x] = max(widths[x], w)
            if not y in heights:
                heights[y] = h
            else:
                heights[y] = max(heights[y], h)
        self._size = sum(widths.values()) + borderSize * 2, sum(heights.values()) + borderSize * 2
        if self._alignBottom:
            y0 -= self._size[1] - self._parent.getSize()[3]
            self._parent.setSize(x0 - borderSize, y0 - borderSize, self._size[0], self._size[1])
        for ctrl in self._parent._glGuiControlList:
            x, y = ctrl._pos
            x1 = x0
            y1 = y0
            for n in xrange(0, x):
                if not n in widths:
                    widths[n] = 3
                x1 += widths[n]
            for n in xrange(0, y):
                if not n in heights:
                    heights[n] = 3
                y1 += heights[n]
            ctrl.setSize(x1, y1, widths[x], heights[y])

    def getLayoutSize(self):
        return self._size


class glButton(glGuiControl):
    def __init__(self, parent, imageID, tooltip, pos, callback, size=None):
        self._buttonSize = size
        self._hidden = False
        super(glButton, self).__init__(parent, pos)
        self._tooltip = tooltip
        self._parent = parent
        self._imageID = imageID
        self._callback = callback
        self._selected = False
        self._focus = False
        self._disabled = False
        self._showExpandArrow = False
        self._progressBar = None
        self._altTooltip = ''

    def isDisabled(self):
        return self._disabled

    def setSelected(self, value):
        self._selected = value

    def setExpandArrow(self, value):
        self._showExpandArrow = value

    def setHidden(self, value):
        self._hidden = value

    def setDisabled(self, value):
        self._disabled = value

    def setCallback(self, value):
        self._callback = value

    def setTooltip(self, value):
        self._tooltip = value

    def setImageID(self, value):
        self._imageID = value

    @QtCore.Slot(float)
    def setProgressBar(self, value):
        if value < 0:
            value = None
        self._progressBar = value

    def getProgressBar(self):
        return self._progressBar

    def setBottomText(self, value):
        self._altTooltip = value

    def getSelected(self):
        return self._selected

    def getMinSize(self):
        if self._hidden:
            return 0, 0
        if self._buttonSize is not None:
            return self._buttonSize, self._buttonSize
        return self._base._buttonSize, self._base._buttonSize

    def _getPixelPos(self):
        x0, y0, w, h = self.getSize()
        return x0 + w / 2, y0 + h / 2

    def draw(self, painter=None):
        if self._hidden:
            return

        bs = self.getMinSize()[0]
        pos = self._getPixelPos()

        glBindTexture(GL_TEXTURE_2D, self._base._glButtonsTexture)
        scale = 0.8
        if self._selected:
            scale = 1.0
        elif self._focus:
            scale = 0.9
        if self._disabled:
            glColor4ub(128,128,128,128)
        else:
            glColor4ub(255,255,255,255)
        openglHelpers.glDrawTexturedQuad(pos[0]-bs*scale/2, pos[1]-bs*scale/2, bs*scale, bs*scale, 0)
        openglHelpers.glDrawTexturedQuad(pos[0]-bs*scale/2, pos[1]-bs*scale/2, bs*scale, bs*scale, self._imageID)
        if self._showExpandArrow:
            if self._selected:
                openglHelpers.glDrawTexturedQuad(pos[0]+bs*scale/2-bs*scale/4*1.2, pos[1]-bs*scale/2*1.2, bs*scale/4, bs*scale/4, 1)
            else:
                openglHelpers.glDrawTexturedQuad(pos[0]+bs*scale/2-bs*scale/4*1.2, pos[1]-bs*scale/2*1.2, bs*scale/4, bs*scale/4, 1, 2)
        glPushMatrix()
        glTranslatef(pos[0], pos[1], 0)
        glDisable(GL_TEXTURE_2D)
        if self._focus:
            glTranslatef(0, -0.55*bs*scale, 0)

            glPushMatrix()
            glColor4ub(60,60,60,255)
            glTranslatef(-1, -1, 0)
            openglHelpers.glDrawStringCenter(self._tooltip)
            glTranslatef(0, 2, 0)
            openglHelpers.glDrawStringCenter(self._tooltip)
            glTranslatef(2, 0, 0)
            openglHelpers.glDrawStringCenter(self._tooltip)
            glTranslatef(0, -2, 0)
            openglHelpers.glDrawStringCenter(self._tooltip)
            glPopMatrix()

            glColor4ub(255,255,255,255)
            openglHelpers.glDrawStringCenter(self._tooltip)
        glPopMatrix()
        progress = self._progressBar
        if progress is not None:
            glColor4ub(60,60,60,255)
            openglHelpers.glDrawQuad(pos[0]-bs/2, pos[1]+bs/2, bs, bs / 4)
            glColor4ub(255,255,255,255)
            openglHelpers.glDrawQuad(pos[0]-bs/2+2, pos[1]+bs/2+2, (bs - 5) * progress + 1, bs / 4 - 4)
        elif len(self._altTooltip) > 0:
            glPushMatrix()
            glTranslatef(pos[0], pos[1], 0)
            glTranslatef(0, 0.6*bs, 0)
            glTranslatef(0, 6, 0)
            #glTranslatef(0.6*bs*scale, 0, 0)

            for line in self._altTooltip.split('\n'):
                glPushMatrix()
                glColor4ub(60,60,60,255)
                glTranslatef(-1, -1, 0)
                openglHelpers.glDrawStringCenter(line)
                glTranslatef(0, 2, 0)
                openglHelpers.glDrawStringCenter(line)
                glTranslatef(2, 0, 0)
                openglHelpers.glDrawStringCenter(line)
                glTranslatef(0, -2, 0)
                openglHelpers.glDrawStringCenter(line)
                glPopMatrix()

                glColor4ub(255,255,255,255)
                openglHelpers.glDrawStringCenter(line)
                glTranslatef(0, 18, 0)
            glPopMatrix()

    def _checkHit(self, x, y):
        if self._hidden or self._disabled:
            return False
        bs = self.getMinSize()[0]
        pos = self._getPixelPos()
        return -bs * 0.5 <= x - pos[0] <= bs * 0.5 and -bs * 0.5 <= y - pos[1] <= bs * 0.5

    def onMouseMoveEvent(self, x, y):
        if self._checkHit(x, y):
            self._focus = True
            return True
        self._focus = False
        return False

    def onMousePressEvent(self, x, y, button):
        if self._checkHit(x, y):
            self._callback(button)
            return True
        return False


class glRadioButton(glButton):
    def __init__(self, parent, imageID, tooltip, pos, group, callback):
        super(glRadioButton, self).__init__(parent, imageID, tooltip, pos, self._onRadioSelect)
        self._group = group
        self._radioCallback = callback
        self._group.append(self)

    def setSelected(self, value):
        self._selected = value

    def _onRadioSelect(self, button):
        self._base._focus = None
        for ctrl in self._group:
            if ctrl != self:
                ctrl.setSelected(False)
        if self.getSelected():
            self.setSelected(False)
        else:
            self.setSelected(True)
        self._radioCallback(button)


class glComboButton(glButton):
    def __init__(self, parent, tooltip, imageIDs, tooltips, pos, callback):
        super(glComboButton, self).__init__(parent, imageIDs[0], tooltip, pos, self._onComboOpenSelect)
        self._allImageIDs = imageIDs
        self._imageIDs = imageIDs[:-1]
        self._tooltips = tooltips
        self._comboCallback = callback
        self._selection = 0

    def _onComboOpenSelect(self, button):
        if self.hasFocus():
            self._base._focus = None
        else:
            self._base._focus = self

    def hide_layers_button(self):
        self._imageIDs = self._allImageIDs[:-1]

    def show_layers_button(self):
        self._imageIDs = self._allImageIDs

    def draw(self, painter=None):
        if self._hidden:
            return
        self._selected = self.hasFocus()
        super(glComboButton, self).draw()

        bs = self._base._buttonSize / 2
        pos = self._getPixelPos()

        if not self._selected:
            return

        glPushMatrix()
        glTranslatef(pos[0]+bs*0.5, pos[1] + bs*0.5, 0)
        glBindTexture(GL_TEXTURE_2D, self._base._glButtonsTexture)
        for n in xrange(0, len(self._imageIDs)):
            glTranslatef(0, bs, 0)
            glColor4ub(255,255,255,255)
            openglHelpers.glDrawTexturedQuad(-0.5*bs,-0.5*bs,bs,bs, 0)
            openglHelpers.glDrawTexturedQuad(-0.5*bs,-0.5*bs,bs,bs, self._imageIDs[n])
            glDisable(GL_TEXTURE_2D)

            glPushMatrix()
            glTranslatef(-0.55*bs, 0.1*bs, 0)

            glPushMatrix()
            glColor4ub(60,60,60,255)
            glTranslatef(-1, -1, 0)
            openglHelpers.glDrawStringRight(self._tooltips[n])
            glTranslatef(0, 2, 0)
            openglHelpers.glDrawStringRight(self._tooltips[n])
            glTranslatef(2, 0, 0)
            openglHelpers.glDrawStringRight(self._tooltips[n])
            glTranslatef(0, -2, 0)
            openglHelpers.glDrawStringRight(self._tooltips[n])
            glPopMatrix()

            glColor4ub(255,255,255,255)
            openglHelpers.glDrawStringRight(self._tooltips[n])
            glPopMatrix()
        glPopMatrix()

    def getValue(self):
        return self._selection

    def setValue(self, value):
        self._selection = value
        self._imageID = self._imageIDs[self._selection]
        self._comboCallback()

    def onMousePressEvent(self, x, y, button):
        if self._hidden or self._disabled:
            return False
        if self.hasFocus():
            bs = self._base._buttonSize / 2
            pos = self._getPixelPos()
            if 0 <= x - pos[0] <= bs and 0 <= y - pos[1] - bs <= bs * len(self._imageIDs):
                self._selection = int((y - pos[1] - bs) / bs)
                self._imageID = self._imageIDs[self._selection]
                self._base._focus = None
                self._comboCallback()
                return True
        return super(glComboButton, self).onMousePressEvent(x, y, button)


class glFrame(glGuiContainer):
    def __init__(self, parent, pos):
        super(glFrame, self).__init__(parent, pos)
        self._selected = False
        self._focus = False
        self._hidden = False

    def setSelected(self, value):
        self._selected = value

    def setHidden(self, value):
        self._hidden = value
        for child in self._glGuiControlList:
            if self._base._focus == child:
                self._base._focus = None

    def getSelected(self):
        return self._selected

    def getMinSize(self):
        return self._base._buttonSize, self._base._buttonSize

    def _getPixelPos(self):
        x0, y0, w, h = self.getSize()
        return x0, y0

    def draw(self, painter=None):
        if self._hidden:
            return

        bs = self._parent._buttonSize
        pos = self._getPixelPos()

        size = self._layout.getLayoutSize()
        glColor4ub(255,255,255,255)
        openglHelpers.glDrawStretchedQuad(pos[0], pos[1], size[0], size[1], bs*0.75, 0)

    def _checkHit(self, x, y):
        if self._hidden:
            return False
        pos = self._getPixelPos()
        w, h = self._layout.getLayoutSize()
        return 0 <= x - pos[0] <= w and 0 <= y - pos[1] <= h

    def onMouseMoveEvent(self, x, y):
        super(glFrame, self).onMouseMoveEvent(x, y)
        if self._checkHit(x, y):
            self._focus = True
            return True
        self._focus = False
        return False

    def onMousePressEvent(self, x, y, button):
        if self._checkHit(x, y):
            super(glFrame, self).onMousePressEvent(x, y, button)
            return True
        return False


class glNotification(glFrame):
    def __init__(self, parent, pos):
        self._anim = None
        super(glNotification, self).__init__(parent, pos)
        glGuiLayoutGrid(self)._alignBottom = False
        self._label = glLabel(self, "Notification", (0, 0))
        self._buttonExtra = glButton(self, 31, "???", (1, 0), self.onExtraButton, 25)
        self._button = glButton(self, 30, "", (2, 0), self.onClose, 25)
        self._padding = glLabel(self, "", (0, 1))
        self.setHidden(True)

    def setSize(self, x, y, w, h):
        w, h = self._layout.getLayoutSize()
        baseSize = self._base.GetSizeTuple()
        if self._anim is not None:
            super(glNotification, self).setSize(baseSize[0] / 2 - w / 2, baseSize[1] - self._anim.getPosition() - self._base._buttonSize * 0.2, 1, 1)
        else:
            super(glNotification, self).setSize(baseSize[0] / 2 - w / 2, baseSize[1] - self._base._buttonSize * 0.2, 1, 1)

    def draw(self, painter=None):
        self.setSize(0,0,0,0)
        self.updateLayout()
        super(glNotification, self).draw()

    def message(self, text, extraButtonCallback = None, extraButtonIcon = None, extraButtonTooltip = None):
        self._anim = animation(self._base, -20, 25, 1)
        self.setHidden(False)
        self._label.setLabel(text)
        self._buttonExtra.setHidden(extraButtonCallback is None)
        self._buttonExtra._imageID = extraButtonIcon
        self._buttonExtra._tooltip = extraButtonTooltip
        self._extraButtonCallback = extraButtonCallback
        self._base.queueRefresh()
        self.updateLayout()

    def onExtraButton(self, button):
        self.onClose(button)
        self._extraButtonCallback()

    def onClose(self, button):
        if self._anim is not None:
            self._anim = animation(self._base, self._anim.getPosition(), -20, 1)
        else:
            self._anim = animation(self._base, 25, -20, 1)


class glLabel(glGuiControl):
    def __init__(self, parent, label, pos):
        self._label = label
        super(glLabel, self).__init__(parent, pos)

    def setLabel(self, label):
        self._label = label

    def getMinSize(self):
        w, h = openglHelpers.glGetStringSize(self._label)
        return w + 10, h + 4

    def _getPixelPos(self):
        x0, y0, w, h = self.getSize()
        return x0, y0

    def draw(self, painter=None):
        x, y, w, h = self.getSize()

        glPushMatrix()
        glTranslatef(x, y, 0)

#       glColor4ub(255,255,255,128)
#       glBegin(GL_QUADS)
#       glTexCoord2f(1, 0)
#       glVertex2f( w, 0)
#       glTexCoord2f(0, 0)
#       glVertex2f( 0, 0)
#       glTexCoord2f(0, 1)
#       glVertex2f( 0, h)
#       glTexCoord2f(1, 1)
#       glVertex2f( w, h)
#       glEnd()

        glTranslate(5, h - 5, 0)
        glColor4ub(255,255,255,255)
        openglHelpers.glDrawStringLeft(self._label)
        glPopMatrix()

    def _checkHit(self, x, y):
        return False

    def onMouseMoveEvent(self, x, y):
        return False

    def onMousePressEvent(self, x, y, button):
        return False


class glNumberCtrl(glGuiControl):
    def __init__(self, parent, value, pos, callback):
        self._callback = callback
        self._value = str(value)
        self._selectPos = 0
        self._maxLen = 6
        self._inCallback = False
        super(glNumberCtrl, self).__init__(parent, pos)

    def setValue(self, value):
        if self._inCallback:
            return
        self._value = str(value)

    def getMinSize(self):
        w, h = openglHelpers.glGetStringSize("VALUES")
        return w + 10, h + 4

    def _getPixelPos(self):
        x0, y0, w, h = self.getSize()
        return x0, y0

    def draw(self, painter=None):
        x, y, w, h = self.getSize()

        glPushMatrix()
        glTranslatef(x, y, 0)

        if self.hasFocus():
            glColor4ub(255,255,255,255)
        else:
            glColor4ub(255,255,255,192)
        glBegin(GL_QUADS)
        glTexCoord2f(1, 0)
        glVertex2f( w, 0)
        glTexCoord2f(0, 0)
        glVertex2f( 0, 0)
        glTexCoord2f(0, 1)
        glVertex2f( 0, h-1)
        glTexCoord2f(1, 1)
        glVertex2f( w, h-1)
        glEnd()

        glTranslate(5, h - 5, 0)
        glColor4ub(0,0,0,255)
        openglHelpers.glDrawStringLeft(self._value)
        if self.hasFocus():
            glTranslate(openglHelpers.glGetStringSize(self._value[0:self._selectPos])[0] - 2, -1, 0)
            openglHelpers.glDrawStringLeft('|')
        glPopMatrix()

    def _checkHit(self, x, y):
        x1, y1, w, h = self.getSize()
        return 0 <= x - x1 <= w and 0 <= y - y1 <= h

    def onMouseMoveEvent(self, x, y):
        return False

    def onMousePressEvent(self, x, y, button):
        if self._checkHit(x, y):
            self.setFocus()
            return True
        return False

    def OnKeyChar(self, c):
        self._inCallback = True
        if c == wx.WXK_LEFT:
            self._selectPos -= 1
            self._selectPos = max(0, self._selectPos)
        if c == wx.WXK_RIGHT:
            self._selectPos += 1
            self._selectPos = min(self._selectPos, len(self._value))
        if c == wx.WXK_UP:
            try:
                value = float(self._value)
            except:
                pass
            else:
                value += 0.1
                self._value = str(value)
                self._callback(self._value)
        if c == wx.WXK_DOWN:
            try:
                value = float(self._value)
            except:
                pass
            else:
                value -= 0.1
                if value > 0:
                    self._value = str(value)
                    self._callback(self._value)
        if c == wx.WXK_BACK and self._selectPos > 0:
            self._value = self._value[0:self._selectPos - 1] + self._value[self._selectPos:]
            self._selectPos -= 1
            self._callback(self._value)
        if c == wx.WXK_DELETE:
            self._value = self._value[0:self._selectPos] + self._value[self._selectPos + 1:]
            self._callback(self._value)
        if c == wx.WXK_TAB or c == wx.WXK_NUMPAD_ENTER or c == wx.WXK_RETURN:
            if wx.GetKeyState(wx.WXK_SHIFT):
                self.focusPrevious()
            else:
                self.focusNext()
        if (ord('0') <= c <= ord('9') or c == ord('.')) and len(self._value) < self._maxLen:
            self._value = self._value[0:self._selectPos] + chr(c) + self._value[self._selectPos:]
            self._selectPos += 1
            self._callback(self._value)
        self._inCallback = False

    def setFocus(self):
        self._base._focus = self
        self._selectPos = len(self._value)
        return True


class glCheckbox(glGuiControl):
    def __init__(self, parent, value, pos, callback):
        self._callback = callback
        self._value = value
        self._selectPos = 0
        self._maxLen = 6
        self._inCallback = False
        super(glCheckbox, self).__init__(parent, pos)

    def setValue(self, value):
        if self._inCallback:
            return
        self._value = str(value)

    def getValue(self):
        return self._value

    def getMinSize(self):
        return 20, 20

    def _getPixelPos(self):
        x0, y0, w, h = self.getSize()
        return x0, y0

    def draw(self, painter=None):
        x, y, w, h = self.getSize()

        glPushMatrix()
        glTranslatef(x, y, 0)

        glColor3ub(255,255,255)
        if self._value:
            openglHelpers.glDrawTexturedQuad(w/2-h/2,0, h, h, 28)
        else:
            openglHelpers.glDrawTexturedQuad(w/2-h/2,0, h, h, 29)

        glPopMatrix()

    def _checkHit(self, x, y):
        x1, y1, w, h = self.getSize()
        return 0 <= x - x1 <= w and 0 <= y - y1 <= h

    def onMouseMoveEvent(self, x, y):
        return False

    def onMousePressEvent(self, x, y, button):
        if self._checkHit(x, y):
            self._value = not self._value
            return True
        return False


class glSlider(glGuiControl):
    def __init__(self, parent, value, minValue, maxValue, pos, callback):
        super(glSlider, self).__init__(parent, pos)
        self._callback = callback
        self._focus = False
        self._hidden = False
        self._value = value
        self._minValue = minValue
        self._maxValue = maxValue

    def setValue(self, value):
        self._value = value

    def getValue(self):
        if self._value < self._minValue:
            return self._minValue
        if self._value > self._maxValue:
            return self._maxValue
        return self._value

    def setRange(self, minValue, maxValue):
        if maxValue < minValue:
            maxValue = minValue
        self._minValue = minValue
        self._maxValue = maxValue

    def getMinValue(self):
        return self._minValue

    def getMaxValue(self):
        return self._maxValue

    def setHidden(self, value):
        self._hidden = value

    def getMinSize(self):
        return self._base._buttonSize * 0.2, self._base._buttonSize * 4

    def _getPixelPos(self):
        x0, y0, w, h = self.getSize()
        minSize = self.getMinSize()
        return x0 + w / 2 - minSize[0] / 2, y0 + h / 2 - minSize[1] / 2

    def draw(self, painter=None):
        if self._hidden:
            return

        w, h = self.getMinSize()
        pos = self._getPixelPos()

        glPushMatrix()
        glTranslatef(pos[0], pos[1], 0)
        glDisable(GL_TEXTURE_2D)
        if self.hasFocus():
            glColor4ub(60,60,60,255)
        else:
            glColor4ub(60,60,60,192)
        glBegin(GL_QUADS)
        glVertex2f( w/2,-h/2)
        glVertex2f(-w/2,-h/2)
        glVertex2f(-w/2, h/2)
        glVertex2f( w/2, h/2)
        glEnd()
        scrollLength = h - w
        if self._maxValue-self._minValue != 0:
            valueNormalized = ((self.getValue()-self._minValue)/(self._maxValue-self._minValue))
        else:
            valueNormalized = 0
        glTranslate(0.0,scrollLength/2,0)
        if True:  # self._focus:
            glColor4ub(0,0,0,255)
            glPushMatrix()
            glTranslate(-w/2,openglHelpers.glGetStringSize(str(self._minValue))[1]/2,0)
            openglHelpers.glDrawStringRight(str(self._minValue))
            glTranslate(0,-scrollLength,0)
            openglHelpers.glDrawStringRight(str(self._maxValue))
            glTranslate(w,scrollLength-scrollLength*valueNormalized,0)
            openglHelpers.glDrawStringLeft(str(self.getValue()))
            glPopMatrix()
        glColor4ub(255,255,255,240)
        glTranslate(0.0,-scrollLength*valueNormalized,0)
        glBegin(GL_QUADS)
        glVertex2f( w/2,-w/2)
        glVertex2f(-w/2,-w/2)
        glVertex2f(-w/2, w/2)
        glVertex2f( w/2, w/2)
        glEnd()
        glPopMatrix()

    def _checkHit(self, x, y):
        if self._hidden:
            return False
        pos = self._getPixelPos()
        w, h = self.getMinSize()
        return -w/2 <= x - pos[0] <= w/2 and -h/2 <= y - pos[1] <= h/2

    def setFocus(self):
        self._base._focus = self
        return True

    def onMouseMoveEvent(self, x, y):
        if self.hasFocus():
            w, h = self.getMinSize()
            scrollLength = h - w
            pos = self._getPixelPos()
            self.setValue(int(self._minValue + (self._maxValue - self._minValue) * -(y - pos[1] - scrollLength/2) / scrollLength))
            self._callback()
            return True
        if self._checkHit(x, y):
            self._focus = True
            return True
        self._focus = False
        return False

    def onMousePressEvent(self, x, y, button):
        if self._checkHit(x, y):
            self.setFocus()
            self.onMouseMoveEvent(x, y)
            return True
        return False

    def onMouseReleaseEvent(self, x, y):
        if self.hasFocus():
            self._base._focus = None
            return True
        return False


class glTempGauge(glGuiControl):
    """
    Custom gauge for displaying temperature value
    """
    def __init__(self, parent, size=(200, 200), pos=(0,0), title="", maxval=240,
            gauge_color=None, bgcolor="#FFFFFF"):
        self._hidden = True
        super(glTempGauge, self).__init__(parent, pos)
        self._parent = parent
        self._width, self._height = size
        self._title = title
        self._maxval = maxval
        self._gauge_color = gauge_color
        self._bgcolor = QtGui.QColor(bgcolor)
        self._value = 0
        self._setpoint = 0
        self._hidden = True
        self.recalc()

    def set_gradient_brush(self, gradient, painter, colors):
        for tup in colors:
            gradient.setColorAt(*tup)
        painter.setBrush(QtGui.QBrush(gradient))

    def set_lineargradient_brush(self, painter, positions, colors):
        """
        positions is tuple of coordinates of start and stop
        colors is a tuple of tuples (position, color)
        """
        gradient = QtGui.QLinearGradient(*positions)
        self.set_gradient_brush(gradient, painter, colors)

    def set_radialgradient_brush(self, painter, positions, colors):
        """
        positions is tuple of start coordinates and radius
        colors is a tuple of tuples (position, color)
        """
        gradient = QtGui.QRadialGradient(*positions)
        self.set_gradient_brush(gradient, painter, colors)

    def set_font(self, painter, size, style, weight):
        font = QtGui.QFont()
        font.setPointSize(size)
        font.setStyle(style)
        font.setWeight(weight)
        painter.setFont(font)

    def draw(self, painter=None):
        if self._hidden or not painter:
            return
        x0, y0 = self.getSize()[:2]
        x1, y1, xE, yE = self._ypt + 1, 1, self._width - 1, 20

        cold = QtGui.QColor(0, 167, 223)
        medium = QtGui.QColor(239, 233, 119)
        hot = QtGui.QColor(210, 50, 100)

        gauge1 = QtGui.QColor(255, 255, 210)
        gauge2 = QtGui.QColor(234, 82, 0)
        shadow1, shadow2 = QtGui.QColor(110, 110, 110), self._bgcolor

        painter.setPen(QtCore.Qt.NoPen)

        # gauge background
        self.set_lineargradient_brush(
                painter,
                (x0, y0, x0 + xE - x1, y0 + yE),
                ((0, cold), (0.5, medium), (1, hot))
                )

        painter.drawRoundedRect(x0, y0, xE - x1, yE, 6, 6)

        # draw initial gauge
        width = 12
        w1 = y0 + yE / 2 - width / 2
        w2 = w1 + width
        value = x0 + max(10, min(self._width - 1, int(self._value * self._scale)))

        self.set_lineargradient_brush(
                painter,
                (x0, y0 + 3, x0, y0 + 15),
                ((0, gauge1), (1, self.interpolatedColour(
                    value, x0, x1, xE, cold, medium, hot)))
                )

        path = QtGui.QPainterPath()
        path.moveTo(x0 - 1, w1)
        path.lineTo(value, w1)
        path.lineTo(value + 2, w1 + width / 4)
        path.lineTo(value + 2, w2 - width / 4)
        path.lineTo(value, w2)
        path.lineTo(x0 - 1, w2)
        painter.drawPath(path)

        # draw setpoint markers
        setpoint = x0 + 2 + max(10, int(self._setpoint * self._scale))
        painter.setBrush(QtGui.QBrush(QtGui.QColor(0, 0, 0)))
        path = QtGui.QPainterPath()
        marker_height = yE/2 - 2

        path.moveTo(setpoint - 4, y0)
        path.lineTo(setpoint + 4, y0)
        path.lineTo(setpoint, y0 + marker_height)

        path.moveTo(setpoint - 4, y0 + yE)
        path.lineTo(setpoint + 4, y0 + yE)
        path.lineTo(setpoint, y0 + yE - marker_height)
        painter.drawPath(path)

        # draw readout
        text = u"T\u00B0 %u/%u" % (self._value, self._setpoint)
        fontsize = 9
        self.set_font(painter, fontsize, QtGui.QFont.StyleNormal, QtGui.QFont.Bold)
        painter.setPen(QtCore.Qt.white)
        textpoint = y0 + yE - fontsize/2
        painter.drawText(x0 + 19, textpoint, self._title)
        painter.drawText(x0 + 119, textpoint, text)

        self.set_font(painter, fontsize, QtGui.QFont.StyleNormal, QtGui.QFont.Bold)
        painter.setPen(QtCore.Qt.black)
        painter.drawText(x0 + 18, textpoint - 1, self._title)
        painter.drawText(x0 + 118, textpoint - 1, text)

        return

    def recalc(self):
        mmax = max(int(self._setpoint * 1.05), self._maxval)
        self._scale = float(self._width - 2) / float(mmax)
        self._ypt = max(16, int(self._scale * max(self._setpoint, self._maxval / 6)))

    def setValue(self, value):
        self._value = value
        self._base.queueRefresh()

    def setTarget(self, value):
        self._setpoint = value
        self._base.queueRefresh()

    def setHidden(self, val):
        self._hidden = val

    def interpolatedColour(self, val, vmin, vmid, vmax, cmin, cmid, cmax):
        if val < vmin: return cmin
        if val > vmax: return cmax
        if val <= vmid:
            lo, hi, val, valhi = cmin, cmid, val - vmin, vmid - vmin
        else:
            lo, hi, val, valhi = cmid, cmax, val - vmid, vmax - vmid
        vv = float(val) / valhi
        rgb = lo.red() + (hi.red() - lo.red()) * vv, lo.green() + \
                (hi.green() - lo.green()) * vv, lo.blue() + \
                (hi.blue() - lo.blue()) * vv
        rgb = map(lambda x: x * 0.8, rgb)
        return QtGui.QColor(*map(int, rgb))

    def onMouseMoveEvent(self, x, y):
        return False

    def onMousePressEvent(self, x, y, button):
        return False


# class glTempGauges(glGuiControl):
#     def __init__(self, parent, pos):
#         super(glTempGauges, self).__init__(parent, pos)
#         self._container = []
# 
#     def add(self, elem):
#         self._container.append(elem)
# 
#     def draw(self, painter=None):
#         for elem in self._container:
#             elem.draw(painter)
# 
#     def onMouseMoveEvent(self, x, y):
#         for elem in self._container:
#             elem.onMouseMoveEvent(x, y)
# 
#     def onMousePressEvent(self, x, y, button):
#         for elem in self._container:
#             elem.onMousePressEvent(x, y, button)
