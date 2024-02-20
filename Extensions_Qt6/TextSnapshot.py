import os

from PyQt6 import QtGui, QtWidgets

from Extensions_Qt6.BaseScintilla import BaseScintilla
from Extensions_Qt6 import Global
from Extensions_Qt6 import StyleSheet


class TextSnapshot(BaseScintilla):

    def __init__(self, useData, colorScheme, fileType, parent=None):
        BaseScintilla.__init__(self, parent)

        self.setFont(Global.getDefaultFont())
        self.setMarginLineNumbers(0, True)
        self.createContextMenu()

        self.DATA = {"fileType": fileType}
        self.setObjectName("editor")
        self.enableMarkOccurrence(useData)

        self.colorScheme = colorScheme
        self.colorScheme.styleEditor(self)

    def updateLexer(self, lexer):
        self.setLexer(lexer)

    def createContextMenu(self):
        self.copyAct = QtGui.QAction(
            "Copy", self, shortcut=QtGui.QKeySequence(QtGui.QKeySequence.StandardKey.Copy),
            statusTip="Copy selected text", triggered=self.copy)

        self.selectAllAct = QtGui.QAction("Select All", self,
                                          shortcut=QtGui.QKeySequence.StandardKey.SelectAll,
                                          statusTip="Select All",
                                          triggered=self.selectAllText)

        self.selectToMatchingBraceAct = \
            QtGui.QAction(QtGui.QIcon(os.path.join("Resources", "images", "text_select")),
                          "Select to Matching Brace", self,
                          statusTip="Select to Matching Brace",
                          triggered=self.selectToMatchingBrace)

        self.contextMenu = QtWidgets.QMenu()
        self.contextMenu.addAction(self.copyAct)
        self.contextMenu.addAction(self.selectAllAct)
        self.contextMenu.addAction(self.selectToMatchingBraceAct)

    def contextMenuEvent(self, event):
        state = self.hasSelectedText()

        self.copyAct.setEnabled(state)
        self.contextMenu.exec(event.globalPos())

    def selectAllText(self):
        self.selectAll()
