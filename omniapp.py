# -*- coding: utf-8 -*-

import sys
from PySide import QtGui

from gui.mainwindow import Ui_MainWindow


class MainWindow(QtGui.QMainWindow):
  def __init__(self, parent=None):
    super(MainWindow, self).__init__(parent)
    self.ui =  Ui_MainWindow()
    self.ui.setupUi(self)


def main():
    app = QtGui.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
   

if __name__ == "__main__":
    main()
