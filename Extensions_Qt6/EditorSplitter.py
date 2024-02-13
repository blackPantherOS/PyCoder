from PyQt6 import QtCore, QtGui, QtWidgets
from Extensions_Qt6.MiniMap import MiniMap

class EditorSplitter(QtWidgets.QWidget):
    def __init__(self, editor, editor2, DATA, editorTabWidget, parent):
        QtWidgets.QWidget.__init__(self, parent)

        self.editorTabWidget = editorTabWidget
        self.DATA = DATA
        self.parent = parent
        self.useData = editor.useData

        self.editor = editor
        self.editor2 = editor2

        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)

        self.splitter = QtWidgets.QSplitter()
        mainLayout.addWidget(self.splitter)
        editor2.hide()

        self.splitter.addWidget(self.editor)
        self.splitter.addWidget(self.editor2)

        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)

        #self.editor.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.editor.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        #self.editor2.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.editor2.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.editor.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        #self.editor.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.editor2.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        #self.editor2.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.editor.modificationChanged.connect(self.textModified)
        self.editor2.modificationChanged.connect(self.textModified)

        if self.useData.SETTINGS["MiniMap"] == "True":
            self.minimap = MiniMap(self.editor, self)
            mainLayout.addWidget(self.minimap)

    def addSplitVertical(self):
        self.splitter.setOrientation(QtCore.Qt.Orientation.Vertical)

    def addSplitHorizontal(self):
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


