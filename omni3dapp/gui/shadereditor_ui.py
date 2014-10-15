# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'shadereditor_ui.ui'
#
# Created: Mon Aug 11 12:22:51 2014
#      by: pyside-uic 0.2.13 running on PySide 1.1.0
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_ShaderEditor(object):
    def setupUi(self, ShaderEditor):
        ShaderEditor.setObjectName("ShaderEditor")
        ShaderEditor.resize(400, 500)
        self.widget = QtGui.QWidget(ShaderEditor)
        self.widget.setGeometry(QtCore.QRect(0, 0, 402, 505))
        self.widget.setObjectName("widget")
        self.verticalLayout = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self._vertex = QtGui.QPlainTextEdit(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._vertex.sizePolicy().hasHeightForWidth())
        self._vertex.setSizePolicy(sizePolicy)
        self._vertex.setMinimumSize(QtCore.QSize(399, 249))
        self._vertex.setObjectName("_vertex")
        self.verticalLayout.addWidget(self._vertex)
        self.line = QtGui.QFrame(self.widget)
        self.line.setFrameShape(QtGui.QFrame.HLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout.addWidget(self.line)
        self._fragment = QtGui.QPlainTextEdit(self.widget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self._fragment.sizePolicy().hasHeightForWidth())
        self._fragment.setSizePolicy(sizePolicy)
        self._fragment.setMinimumSize(QtCore.QSize(399, 249))
        self._fragment.setObjectName("_fragment")
        self.verticalLayout.addWidget(self._fragment)

        self.retranslateUi(ShaderEditor)
        QtCore.QMetaObject.connectSlotsByName(ShaderEditor)

    def retranslateUi(self, ShaderEditor):
        ShaderEditor.setWindowTitle(QtGui.QApplication.translate("ShaderEditor", "Shader editor", None, QtGui.QApplication.UnicodeUTF8))
