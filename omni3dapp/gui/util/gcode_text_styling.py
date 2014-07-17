# -*- coding: utf-8 -*-

from PySide import QtCore, QtGui


class GCodeSyntaxHighlighter(QtGui.QSyntaxHighlighter):

    def highlightBlock(self, text):
        comment_format = QtGui.QTextCharFormat()
        comment_format.setForeground(QtCore.Qt.darkGreen)

        comment_pattern = ';.+(?:$|\n)'
        expression = QtCore.QRegExp(comment_pattern)
        index = expression.indexIn(text)
        while index >= 0:
            length = expression.matchedLength()
            self.setFormat(index, length, comment_format)
            index = expression.indexIn(text, index + length)
