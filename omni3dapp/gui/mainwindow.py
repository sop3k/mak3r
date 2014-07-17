# -*- coding: utf-8 -*-

from PySide import QtCore, QtGui

from mainwindow_ui import Ui_MainWindow
from omni3dapp.util.profile import settingsDictionary
from omni3dapp.gui.util.gcode_text_styling import GCodeSyntaxHighlighter
from omni3dapp.logger import log


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.set_up_fields()

    def set_up_fields(self):
        for key, val in settingsDictionary.iteritems():
            elem = getattr(self.ui, key, None)
            if not elem:
                continue
            try:
                if isinstance(elem, (QtGui.QLineEdit, QtGui.QTextEdit)):
                    # Add syntax styling to gcode fields
                    if key.endswith('gcode'):
                        GCodeSyntaxHighlighter(elem)
                    elem.setText(val.getValue())
                elif isinstance(elem, QtGui.QCheckBox):
                    elem.setChecked(val.getValue() == u'True')
                elif isinstance(elem, QtGui.QComboBox):
                    items = val.getType()
                    elem.addItems(items)
                    elem.setCurrentIndex(items.index(val.getValue()))
                elem.setToolTip(val.getTooltip())
            except Exception, e:
                log.debug('Could not set value to field {0}: {1}'.format(key, e))
