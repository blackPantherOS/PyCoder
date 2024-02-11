from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QHBoxLayout,
    QSplitter,
    QSplitterHandle,
    QTabWidget,
    QWidget,
)

from Extensions_Qt6.MiniMap import MiniMap

class CustomSplitter(QSplitter):
    @property
    def enabled(self):
        if not hasattr(self, "_enabled"):
            self._enabled = True
        return self._enabled

    @enabled.setter
    def enabled(self, d):
        self._enabled = d
        for i in range(self.count()):
            self.handle(i).setEnabled(self.enabled)

    def createHandle(self):
        handle = super().createHandle()
        handle.setEnabled(self.enabled)
        return handle

class EditorSplitter(QtWidgets.QWidget):
    def __init__(self, editor, editor2, DATA, editorTabWidget, parent):
        QtWidgets.QWidget.__init__(self, parent)

        self.editorTabWidget = editorTabWidget
        self.DATA = DATA
        self.parent = parent

        self.editor = editor
        self.editor2 = editor2

        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)

        self.splitter = QtWidgets.QSplitter()
        #self.splitter = CustomSplitter()
        mainLayout.addWidget(self.splitter)
        editor2.hide()

        self.splitter.addWidget(self.editor)
        self.splitter.addWidget(self.editor2)

        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)

        self.editor.modificationChanged.connect(self.textModified)
        self.editor2.modificationChanged.connect(self.textModified)

        self.minimap = MiniMap(self.editor, self)
        mainLayout.addWidget(self.minimap)

    def splitVertical(self):
        self.splitter.setOrientation(QtCore.Qt.Orientation.Vertical)

    def splitHorizontal(self):
        self.splitter.setOrientation(QtCore.Qt.Orientation.Horizontal)

    def getEditor(self, index=None):
        if index is None:
            index = 0
        return self.splitter.widget(index)

    def getFocusedEditor(self):
        f = self.splitter.focusWidget()
        if f is None:
            return self.getEditor()
        return f

    def textModified(self, modified):
        index = self.editorTabWidget.indexOf(self.parent)
        self.editorTabWidget.updateTabName(index)
