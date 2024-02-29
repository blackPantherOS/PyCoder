import os
from PyQt6 import QtCore, QtGui, QtWidgets

class SearchWidget(QtWidgets.QLabel):

    def __init__(self, useData, editorTabWidget, parent=None):
        QtWidgets.QDialog.__init__(self, parent)

        self.useData = useData
        self.editorTabWidget = editorTabWidget

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setContentsMargins(5, 0, 0, 0)

        self.createFindWidget()
        self.createReplaceWidget()

        self.setLayout(self.mainLayout)

        self.matchCase = False
        self.matchWholeWord = False
        self.matchRegExp = False
        self.wrapAround = False

        self.hide()

    def createFindWidget(self):
        self.textFinderWidget = QtWidgets.QWidget()

        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addWidget(QtWidgets.QLabel(_("Find:")))

        self.findLine = QtWidgets.QLineEdit()
        self.findLine.textEdited.connect(self.find)
        self.previousWordLength = 0
        hbox.addWidget(self.findLine)

        self.findDownButton = QtWidgets.QToolButton()
        self.findDownButton.setAutoRaise(True)
        self.findDownButton.setIconSize(QtCore.QSize(20, 20))
        self.findDownButton.setDefaultAction(
            QtGui.QAction(
                QtGui.QIcon(os.path.join("Resources", "images", "findDown")),
                _("Find Next"), self, triggered=self.findNext))
        hbox.addWidget(self.findDownButton)

        #vector bellow solved: self.findLine.returnPressed.connect(self.findNext)

        self.findUpButton = QtWidgets.QToolButton()
        self.findUpButton.setAutoRaise(True)
        self.findUpButton.setIconSize(QtCore.QSize(20, 20))
        self.findUpButton.setDefaultAction(
            QtGui.QAction(
                QtGui.QIcon(os.path.join("Resources", "images", "findUp")),
                _("Find Previous"), self,
                triggered=self.findPrevious))
        hbox.addWidget(self.findUpButton)

        self.matchCaseBox = QtWidgets.QCheckBox(_("MC"))
        self.matchCaseBox.setToolTip(_("Match Case"))
        self.matchCaseBox.stateChanged.connect(self.updateFindOptions)
        hbox.addWidget(self.matchCaseBox)

        self.matchWholeWordBox = QtWidgets.QCheckBox(_("WW"))
        self.matchWholeWordBox.setToolTip(_("Whole Word"))
        self.matchWholeWordBox.stateChanged.connect(
            self.updateFindOptions)
        hbox.addWidget(self.matchWholeWordBox)

        self.matchRegExpBox = QtWidgets.QCheckBox(_("RE"))
        self.matchRegExpBox.setToolTip(_("Regular Expression"))
        self.matchRegExpBox.stateChanged.connect(self.updateFindOptions)
        hbox.addWidget(self.matchRegExpBox)

        self.wrapAroundBox = QtWidgets.QCheckBox(_("WA"))
        self.wrapAroundBox.setToolTip(_("Wrap Around"))
        self.wrapAroundBox.stateChanged.connect(self.updateFindOptions)
        hbox.addWidget(self.wrapAroundBox)

        hbox.addStretch(1)

        self.hideFindWidgetButton = QtWidgets.QToolButton()
        self.hideFindWidgetButton.setAutoRaise(True)
        self.hideFindWidgetButton.setIcon(
            QtGui.QIcon(os.path.join("Resources", "images", "exit")))
        self.hideFindWidgetButton.clicked.connect(self.hideFindWidget)
        hbox.addWidget(self.hideFindWidgetButton)

        self.textFinderWidget.setLayout(hbox)
        hbox.setStretch(1, 1)
        self.mainLayout.addWidget(self.textFinderWidget)

    def keyPressEvent(self, e):
        if e.modifiers() == QtCore.Qt.KeyboardModifier.ShiftModifier and e.key() == QtCore.Qt.Key.Key_Return:
            self.findPrevious()
            return
        elif e.key() == QtCore.Qt.Key.Key_Return:
            self.findNext()
        else:
            pass

    def createReplaceWidget(self):
        self.replacerWidget = QtWidgets.QWidget()

        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.addStretch(1)

        label = QtWidgets.QLabel(_("Replace with:"))
        hbox.addWidget(label)

        self.replaceLine = QtWidgets.QLineEdit()
        hbox.addWidget(self.replaceLine)

        self.replaceButton = QtWidgets.QPushButton(_("Replace"))
        self.replaceButton.clicked.connect(self.replace)
        hbox.addWidget(self.replaceButton)

        self.replaceAllButton = QtWidgets.QPushButton(_("Replace All"))
        self.replaceAllButton.clicked.connect(self.replaceAll)
        hbox.addWidget(self.replaceAllButton)

        hbox.addStretch(1)

        self.replacerWidget.setLayout(hbox)
        hbox.setStretch(2, 1)
        self.mainLayout.addWidget(self.replacerWidget)

    def showFinder(self):
        self.mainLayout.setContentsMargins(5, 0, 5, 0)
        self.setMinimumHeight(30)
        self.setMaximumHeight(30)
        self.replacerWidget.hide()

        self.show()
        self.fixTextAtCursor()
        self.textFinderWidget.show()
        self.findLine.selectAll()
        self.findLine.setFocus()

    def fixTextAtCursor(self):
        editor = self.editorTabWidget.focusedEditor()
        self.findLine.selectAll()
        if editor.hasSelectedText():
            selection = editor.selectedText()
            self.findLine.insert(selection)

    def showReplaceWidget(self):
        self.mainLayout.setContentsMargins(5, 5, 5, 5)
        self.setMinimumHeight(70)
        self.setMaximumHeight(70)
        self.findLine.setText(self.editorTabWidget.get_current_word())
        self.show()
        self.fixTextAtCursor()
        self.replacerWidget.show()
        self.findLine.selectAll()
        self.findLine.setFocus()

    def hideFindWidget(self):
        self.hide()

    def updateFindOptions(self):
        self.matchCase = self.matchCaseBox.isChecked()
        self.matchWholeWord = self.matchWholeWordBox.isChecked()
        self.matchRegExp = self.matchRegExpBox.isChecked()
        self.wrapAround = self.wrapAroundBox.isChecked()

        self.find()

    def find(self):
        text = self.findLine.text()
        editor = self.editorTabWidget.focusedEditor()
        if text == '':
            self.findLine.setStyleSheet(
                "QLineEdit {border-bottom: 1px solid lightblue;}")
            editor.clearAllIndicators(editor.searchIndicator)
        else:
            if self.useData.SETTINGS['DynamicSearch'] == 'True':
                editor.clearAllIndicators(editor.searchIndicator)
                found = editor.findFirst(text, self.matchRegExp,
                                         self.matchCase, self.matchWholeWord, self.wrapAround, True, 0, 0, True)
                if found:
                    self.findLine.setStyleSheet(
                        "QLineEdit {border-bottom: 1px solid lightgreen;}")
                else:
                    self.findLine.setStyleSheet(
                        "QLineEdit {border-bottom: 2px solid #FF6666;}")

    def findNext(self):
        text = self.findLine.text()
        editor = self.editorTabWidget.focusedEditor()
        if text == '':
            pass
        else:
            editor.findFirst(text, self.matchRegExp,
                             self.matchCase, self.matchWholeWord, self.wrapAround,
                             True, -1, -1, True)

    def findPrevious(self):
        text = self.findLine.text()
        editor = self.editorTabWidget.focusedEditor()
        if text == '':
            pass
        else:
            editor.findFirst(text, self.matchRegExp,
                             self.matchCase, self.matchWholeWord,
                             self.wrapAround, False, -1, -1, True)
            editor.findNext()

    def replace(self):
        # FIXME Text replace only works after finding next
        # not after finding previous
        text = self.findLine.text()
        replaceText = self.replaceLine.text()
        editor = self.editorTabWidget.focusedEditor()
        if editor.hasSelectedText():
            pass
        else:
            editor.findFirst(text, self.matchRegExp,
                             self.matchCase, self.matchWholeWord, self.wrapAround,
                             True, -1, -1, True)
        editor.replace(replaceText)
        found = editor.findFirst(text, self.matchRegExp,
                                 self.matchCase, self.matchWholeWord, self.wrapAround,
                                 True, -1, -1, True)

    def replaceAll(self):
        text = self.findLine.text()
        replaceText = self.replaceLine.text()
        editor = self.editorTabWidget.focusedEditor()
        editor.setCursorPosition(0, 0)
        find = editor.findFirst(text,
                                self.matchRegExp,
                                self.matchCase, self.matchWholeWord, self.wrapAround,
                                True, 1, 1, True)
        editor.beginUndoAction()
        while find:
            editor.replace(replaceText)
            find = editor.findNext()
        editor.endUndoAction()
