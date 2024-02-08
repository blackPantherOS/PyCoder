import os
import re
# FIXME QtXml is no longer supported.
from PyQt6 import QtCore, QtGui, QtWidgets, QtXml


class FinderThread(QtCore.QThread):

    searchSoFar = QtCore.pyqtSignal(int)

    def find(self, text, matchCase, matchWholeWord, regExp, searchLoc, libraryDir):
        self.text = text
        self.cs = matchCase
        self.wo = matchWholeWord
        self.reg = regExp
        self.searchLoc = searchLoc
        self.libraryDir = libraryDir

        self.stop = False
        self.found = []

        self.start()

    def run(self):
        self.found = []
        if self.reg:
            txt = self.text
        else:
            txt = re.escape(self.text)
        if self.wo:
            txt = "\\b{0}\\b".format(txt)
        flags = re.UNICODE | re.LOCALE
        if not self.cs:
            flags |= re.IGNORECASE
        try:
            search = re.compile(txt, flags)
        except re.error as why:
            print(why)

        files = os.listdir(self.libraryDir)
        # FIXME QtXml is no longer supported.
        dom_document = QtXml.QDomDocument()
        for i in range(len(files)):
            if self.stop:
                break
            file = os.path.abspath(os.path.join(self.libraryDir, files[i]))

            try:
                text = open(file, 'r').read()
            except:
                continue
            dom_document.setContent(text)

            documentElement = dom_document.documentElement()
            childElement = documentElement.firstChild().toElement()
            while childElement.isNull() is False:
                if childElement.nodeName() == 'comments':
                    if (self.searchLoc == 0) or (self.searchLoc == 2):
                        comments = childElement.firstChild().nodeValue()
                        contains = search.search(comments)
                        if contains:
                            self.found.append(files[i])
                elif childElement.nodeName() == 'code':
                    if (self.searchLoc == 0) or (self.searchLoc == 1):
                        code = childElement.firstChild().nodeValue()
                        contains = search.search(code)
                        if contains:
                            if files[i] not in self.found:
                                self.found.append(files[i])
                childElement = childElement.nextSibling()
            self.searchSoFar.emit(i)

    def stopFind(self):
        self.stop = True

class AdvancedSearch(QtWidgets.QWidget):

    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self, parent, QtCore.Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle("Advanced Search")
        self.resize(400, 120)

        self.library = parent
        self.finderThread = FinderThread()

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)

        self.searchResultsListWidget = QtWidgets.QListWidget()
        self.searchResultsListWidget.itemPressed.connect(
            self.library.viewSearchItem)
        self.searchResultsListWidget.itemActivated.connect(
            self.library.viewSearchItem)
        mainLayout.addWidget(self.searchResultsListWidget)

        mainLayout.addWidget(QtWidgets.QLabel("Find:"))

        self.searchLine = QtWidgets.QLineEdit()
        self.searchLine.returnPressed.connect(self.startSearch)
        mainLayout.addWidget(self.searchLine)

        mainLayout.addWidget(QtWidgets.QLabel("Location:"))

        self.searchLocBox = QtWidgets.QComboBox()
        self.searchLocBox.addItem("Comments AND Source Code")
        self.searchLocBox.addItem("Source Code")
        self.searchLocBox.addItem("Comments")
        mainLayout.addWidget(self.searchLocBox)

        hbox = QtWidgets.QHBoxLayout()

        self.matchCaseBox = QtWidgets.QCheckBox("Match Case")
        hbox.addWidget(self.matchCaseBox)

        self.matchWholeWordBox = QtWidgets.QCheckBox("Whole Word")
        hbox.addWidget(self.matchWholeWordBox)

        self.regExpBox = QtWidgets.QCheckBox("Regular Expression")
        hbox.addWidget(self.regExpBox)

        mainLayout.addLayout(hbox)

        frame = QtWidgets.QFrame()
        frame.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        frame.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        mainLayout.addWidget(frame)

        hbox = QtWidgets.QHBoxLayout()

        self.searchLabel = QtWidgets.QLabel("Searching...")
        hbox.addWidget(self.searchLabel)

        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setMaximumHeight(15)
        self.progressBar.setMinimumWidth(100)
        hbox.addWidget(self.progressBar)

        self.searchLabel.hide()
        self.progressBar.hide()

        self.foundLabel = QtWidgets.QLabel()
        hbox.addWidget(self.foundLabel)
        self.foundLabel.hide()

        hbox.addStretch(1)

        searchButton = QtWidgets.QPushButton("Search")
        searchButton.clicked.connect(self.startSearch)
        hbox.addWidget(searchButton)

        mainLayout.addLayout(hbox)

        mainLayout.setStretch(0, 1)

        self.setLayout(mainLayout)

        self.finderThread.searchSoFar.connect(self.updateProgress)
        self.finderThread.started.connect(self.searchStarted)
        self.finderThread.finished.connect(self.searchStopped)

    def startSearch(self):
        searchText = self.searchLine.text()
        self.progressBar.setMaximum(len(os.listdir(
            self.library.useData.appPathDict["librarydir"])))
        self.finderThread.find(searchText, self.matchCaseBox.isChecked(),
                               self.matchWholeWordBox.isChecked(),
                               self.regExpBox.isChecked(),
                               self.searchLocBox.currentIndex(),
                               self.library.useData.appPathDict["librarydir"])

    def searchStarted(self):
        self.foundLabel.hide()
        self.searchLabel.show()
        self.progressBar.setValue(0)
        self.progressBar.show()

    def searchStopped(self):
        self.searchLabel.hide()
        self.progressBar.hide()
        self.foundLabel.show()
        self.foundLabel.setText(str(len(self.finderThread.found)) + " found!")

        self.searchResultsListWidget.clear()
        for i in self.finderThread.found:
            self.searchResultsListWidget.addItem(QtWidgets.QListWidgetItem(i))

    def updateProgress(self, value):
        self.progressBar.setValue(value)
