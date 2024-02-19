import os
import shutil
# FIXME QtXml is no longer supported.
from PyQt6 import QtCore, QtGui, QtPrintSupport, QtWidgets, QtXml
#from PyQt6.QtCore import Qt

from Extensions_Qt6.Library.LibraryAddDialog import LibraryAddDialog
from Extensions_Qt6.Library.AdvancedSearch import AdvancedSearch
from Extensions_Qt6.BaseScintilla import BaseScintilla


def sizeformat(size):
    byteSize = len(str(size))
    if byteSize < 4:
        return str(size) + "Bytes"
    elif 3 < byteSize < 7:
        return str(round(size / 1024, 2)) + "KB"
    elif 6 < byteSize < 10:
        return str(round(size / 1048576, 2)) + "MB"
    else:
        return str(round(size / 1073741824, 2)) + "GB"


class EditComment(QtWidgets.QDialog):

    def __init__(self, text, parent=None):
        QtWidgets.QDialog.__init__(self, parent, QtCore.Qt.WindowType.Window | QtCore.Qt.WindowType.WindowCloseButtonHint)

        self.resize(400, 200)
        self.setWindowTitle("Edit Comment")

        mainLayout = QtWidgets.QVBoxLayout()

        self.commentEdit = QtWidgets.QPlainTextEdit()
        self.commentEdit.setPlainText(text)
        mainLayout.addWidget(self.commentEdit)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)

        self.okButton = QtWidgets.QPushButton("OK")
        self.okButton.clicked.connect(self.accept)
        hbox.addWidget(self.okButton)

        self.cancelButton = QtWidgets.QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.close)
        hbox.addWidget(self.cancelButton)

        mainLayout.addLayout(hbox)

        self.setLayout(mainLayout)

        self.accepted = False

    def accept(self):
        self.close()
        self.accepted = True


class GetName(QtWidgets.QDialog):

    def __init__(self, caption, path, defaultText=None, parent=None):
        QtWidgets.QDialog.__init__(self, parent, QtCore.Qt.WindowType.Window | QtCore.Qt.WindowType.WindowCloseButtonHint)


        self.setWindowTitle(caption)

        self.path = path

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(QtWidgets.QLabel("Name:"))

        self.nameLine = QtWidgets.QLineEdit()
        if defaultText is not None:
            self.nameLine.setText(defaultText)
            self.nameLine.selectAll()
        self.nameLine.textChanged.connect(self.enableAcceptButton)
        mainLayout.addWidget(self.nameLine)

        hbox = QtWidgets.QHBoxLayout()

        self.statusLabel = QtWidgets.QLabel()
        hbox.addWidget(self.statusLabel)

        self.statusLabel = QtWidgets.QLabel("")
        hbox.addWidget(self.statusLabel)

        hbox.addStretch(1)

        self.acceptButton = QtWidgets.QPushButton("Ok")
        self.acceptButton.setDisabled(True)
        self.acceptButton.clicked.connect(self.accept)
        hbox.addWidget(self.acceptButton)

        self.cancelButton = QtWidgets.QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.close)
        hbox.addWidget(self.cancelButton)

        mainLayout.addLayout(hbox)

        self.setLayout(mainLayout)

        self.resize(300, 20)
        self.enableAcceptButton()

        self.accepted = False

        self.exec_()

    def enableAcceptButton(self):
        text = self.nameLine.text().strip()
        if text == '':
            self.acceptButton.setDisabled(True)
        else:
            preExistNames = os.listdir(self.path)
            if text in preExistNames:
                self.statusLabel.setText("Unavailable")
                self.acceptButton.setDisabled(True)
            else:
                self.statusLabel.setText("Available")
                self.acceptButton.setDisabled(False)

    def accept(self):
        self.accepted = True
        self.name = self.nameLine.text().strip()
        self.close()


class CodeViewer(BaseScintilla):

    def __init__(self, parent=None):
        BaseScintilla.__init__(self, parent)

        self.setReadOnly(True)
        self.setMarginLineNumbers(0, True)
        self.setCaretLineVisible(True)

        self.DATA = {"fileType": "python"}

        self.setStyleSheet("""

                 QsciScintilla {
                         border: none;
                         border-top: 1px solid grey;
                 }

                              """)

    def updateLexer(self, lexer):
        self.setLexer(lexer)


class Library(QtWidgets.QMainWindow):
    def __init__(self, useData):
        super().__init__()

        self.useData = useData
        
        self.mainSplitter = QtWidgets.QSplitter()

        self.advancedSearch = AdvancedSearch(self)

        # define the font to use
        self.font = QtGui.QFont("Courier New")
        self.font.setFixedPitch(True)
        self.font.setPointSize(10)
        self.fontMetrics = QtGui.QFontMetrics(self.font)

        self.codeViewer = CodeViewer()
        self.mainSplitter.addWidget(self.codeViewer)

        #self.subSplitter = QtWidgets.QSplitter(QtWidgets.QSplitter.Orientation.Vertical)
        #self.subSplitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        #self.subSplitter = QtWidgets.QSplitter(Qt.Vertical)
        #self.subSplitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.subSplitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Vertical)

        widget = QtWidgets.QWidget()
        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 5, 0)

        self.tabWidget = QtWidgets.QTabWidget()

        self.libraryCountLabel = QtWidgets.QLabel()
        self.tabWidget.setCornerWidget(self.libraryCountLabel)

        snippetsWidget = QtWidgets.QWidget()
        snippetsVbox = QtWidgets.QVBoxLayout()
        snippetsVbox.setContentsMargins(0, 0, 0, 0)

        self.snippetsListWidget = QtWidgets.QTreeWidget()
        self.snippetsListWidget.setAutoScroll(False)
        self.snippetsListWidget.setRootIsDecorated(True)
        self.snippetsListWidget.setHeaderLabels(["Name", "Size"])
        self.snippetsListWidget.setColumnWidth(0, 300)
        self.snippetsListWidget.itemPressed.connect(self.viewLibraryItem)
        self.snippetsListWidget.itemPressed.connect(self.selectionChanged)
        self.snippetsListWidget.itemActivated.connect(self.viewLibraryItem)
        self.snippetsListWidget.setStyleSheet("""
                    QTreeView {
                         show-decoration-selected: 1; /* make the selection span the entire width of the view */
                         border: none;
                    }
                    """ )
        self.snippetsListWidget.itemSelectionChanged.connect(
            self.selectionChanged)
        snippetsVbox.addWidget(self.snippetsListWidget)

        snippetsWidget.setLayout(snippetsVbox)

        self.tabWidget.addTab(snippetsWidget,
                              QtGui.QIcon(os.path.join("Resources", "images", "envelope")), "Modules")
        self.tabWidget.addTab(self.advancedSearch,
                              QtGui.QIcon(os.path.join("Resources", "images", "search")), "Search")

        vbox.addWidget(self.tabWidget)
        widget.setLayout(vbox)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 5)
        vbox.addLayout(hbox)

        self.showDetailsButton = QtWidgets.QToolButton()
        self.showDetailsButton.setAutoRaise(True)
        self.showDetailsButton.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonFollowStyle)
        self.showDetailsButton.setText("More")
        self.showDetailsButton.setIcon(QtGui.QIcon(
            os.path.join("Resources", "images", "extender-up")))
        self.showDetailsButton.clicked.connect(self.showComments)
        hbox.addWidget(self.showDetailsButton)

        hbox.addStretch(1)

        self.alphaSearchBox = QtWidgets.QComboBox()
        self.alphaSearchBox.setMinimumWidth(73)
        self.alphaSearchBox.activated.connect(self.gotoAlpha)
        hbox.addWidget(self.alphaSearchBox)

        self.subSplitter.addWidget(widget)

        self.detailsWidget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 5, 5, 0)

        layout.addWidget(QtWidgets.QLabel("Comments:"))

        self.commentViewer = QtWidgets.QPlainTextEdit()
        self.commentViewer.setReadOnly(True)
        layout.addWidget(self.commentViewer)

        layout.addWidget(QtWidgets.QLabel("Source:"))

        self.sourceLine = QtWidgets.QLineEdit()
        self.sourceLine.setReadOnly(True)
        layout.addWidget(self.sourceLine)

        self.detailsWidget.setLayout(layout)
        self.detailsWidget.hide()

        self.subSplitter.addWidget(self.detailsWidget)
        self.mainSplitter.addWidget(self.subSplitter)

        self.setCentralWidget(self.mainSplitter)
        # create menu widget
        menuWidget = QtWidgets.QLabel()
        menuWidget.setMinimumHeight(30)
        menuWidget.setScaledContents(True)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(5, 0, 5, 0)

        self.createActions()

        self.exportButton = QtWidgets.QToolButton()
        self.exportButton.setAutoRaise(True)
        self.exportButton.setDefaultAction(self.exportAct)
        hbox.addWidget(self.exportButton)

        self.renameButton = QtWidgets.QToolButton()
        self.renameButton.setAutoRaise(True)
        self.renameButton.setDefaultAction(self.renameAct)
        hbox.addWidget(self.renameButton)

        self.printButton = QtWidgets.QToolButton()
        self.printButton.setAutoRaise(True)
        self.printButton.setDefaultAction(self.printAct)
        hbox.addWidget(self.printButton)

        self.editCommentButton = QtWidgets.QToolButton()
        self.editCommentButton.setAutoRaise(True)
        self.editCommentButton.setDefaultAction(self.editCommentAct)
        hbox.addWidget(self.editCommentButton)

        self.removeButton = QtWidgets.QToolButton()
        self.removeButton.setAutoRaise(True)
        self.removeButton.setDefaultAction(self.removeAct)
        hbox.addWidget(self.removeButton)

        hbox.addStretch(1)

        self.toggleSidebarViewButton = QtWidgets.QToolButton()
        self.toggleSidebarViewButton.setAutoRaise(True)
        self.toggleSidebarViewButton.setDefaultAction(
            self.toggleSidebarViewAct)
        hbox.addWidget(self.toggleSidebarViewButton)

        menuWidget.setLayout(hbox)
        self.setMenuWidget(menuWidget)

        # create StatusBar
        self.statusbar = self.statusBar()

        self.currentSnippetNameLabel = QtWidgets.QLabel()
        self.currentSnippetNameLabel.setIndent(5)
        self.statusbar.addWidget(self.currentSnippetNameLabel)

        self.loadLibrary()
        self.selectionChanged()

    def createActions(self):
        self.editCommentAct = ...
        # Define other actions here as well...

    def createActions(self):
        self.editCommentAct = \
            QtGui.QAction(
                QtGui.QIcon(os.path.join("Resources", "images", "edit")),
                "Edit Comment", self,
                statusTip="Edit Comment", triggered=self.editComment)

        self.removeAct = \
            QtGui.QAction(
                QtGui.QIcon(os.path.join("Resources", "images", "remove")),
                "Remove", self,
                statusTip="Remove", triggered=self.removeItem)

        self.renameAct = \
            QtGui.QAction(
                QtGui.QIcon(
                    os.path.join("Resources", "images", "ui-text-field")),
                "Rename", self,
                statusTip="Rename", triggered=self.rename)

        self.printAct = \
            QtGui.QAction(
                QtGui.QIcon(
                    os.path.join("Resources", "images", "_0013_Printer")),
                "Print", self,
                statusTip="Print", triggered=self.printFile)

        self.exportAct = \
            QtGui.QAction(
                QtGui.QIcon(os.path.join("Resources", "images", "archive")),
                "Export Library", self,
                statusTip="Export Library", triggered=self.export)

        self.toggleSidebarViewAct = \
            QtGui.QAction(
                QtGui.QIcon(os.path.join("Resources", "images", "out")),
                "Toggle Sidebar View", self,
                statusTip="Toggle Sidebar View", triggered=self.viewSideBar)

    def gotoAlpha(self):
        alpha = self.alphaSearchBox.currentText()
        found = self.snippetsListWidget.findItems(alpha,
                                                  QtCore.Qt.MatchStartsWith | QtCore.Qt.MatchCaseSensitive)
        item = found[0]
        self.snippetsListWidget.setCurrentItem(item)
        self.snippetsListWidget.scrollToItem(item, 3)

    def selectionChanged(self):
        selected = self.snippetsListWidget.selectedItems()
        if len(selected) == 0:
            self.removeButton.setDisabled(True)
            self.renameButton.setDisabled(True)
            self.printButton.setDisabled(True)
            self.editCommentButton.setDisabled(True)
        else:
            if selected[0].type() == 1:
                self.removeButton.setDisabled(False)
                self.renameButton.setDisabled(False)
                self.printButton.setDisabled(False)
                self.editCommentButton.setDisabled(False)
            else:
                self.removeButton.setDisabled(True)
                self.renameButton.setDisabled(True)
                self.printButton.setDisabled(True)
                self.editCommentButton.setDisabled(True)

    def findSnippet(self):
        text = self.searchLine.text().strip()
        found = self.snippetsListWidget.findItems(text,
                                                  QtCore.Qt.MatchStartsWith | QtCore.Qt.MatchRecursive |
                                                  QtCore.Qt.MatchCaseSensitive)
        if len(found) != 0:
            item = found[0]
            self.snippetsListWidget.setCurrentItem(item)
            self.snippetsListWidget.scrollToItem(item, 3)

    def editComment(self):
        edit = EditComment(self.commentViewer.toPlainText(), self)
        edit.exec_()

        if edit.accepted:
            comment = edit.commentEdit.toPlainText()
            source = self.sourceLine.text()
            snippetName = self.currentSnippetNameLabel.text()
            path = os.path.join(self.useData.appPathDict[
                                "librarydir"], snippetName)

            # FIXME QtXml is no longer supported.
            dom_document = QtXml.QDomDocument()
            file = open(path, "r")
            dom_document.setContent(file.read())
            file.close()

            # save changes
            # FIXME QtXml is no longer supported.
            dom_document = QtXml.QDomDocument("snippet")
            root = dom_document.createElement("snippet")
            dom_document.appendChild(root)

            tag = dom_document.createElement('comments')
            root.appendChild(tag)

            t = dom_document.createCDATASection(comment)
            tag.appendChild(t)

            tag = dom_document.createElement('source')
            root.appendChild(tag)

            t = dom_document.createCDATASection(source)
            tag.appendChild(t)

            tag = dom_document.createElement('code')
            root.appendChild(tag)

            t = dom_document.createCDATASection(self.codeViewer.text())
            tag.appendChild(t)

            file = open(path, "w")
            file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            file.write(dom_document.toString())
            file.close()
            self.viewLibraryItem(self.currentSnippetItem)

    def showComments(self):
        if self.commentViewer.isVisible():
            self.detailsWidget.hide()
            self.showDetailsButton.setText("More")
            self.showDetailsButton.setIcon(QtGui.QIcon(
                os.path.join("Resources", "images", "extender-up")))
        else:
            self.detailsWidget.show()
            self.showDetailsButton.setText("Less")
            self.showDetailsButton.setIcon(QtGui.QIcon(
                os.path.join("Resources", "images", "extender-down")))

    def viewSideBar(self):
        if self.subSplitter.isHidden() is False:
            self.subSplitter.hide()
            self.toggleSidebarViewAct.setIcon(
                QtGui.QIcon(os.path.join("Resources", "images", "in")))
        else:
            self.subSplitter.show()
            self.toggleSidebarViewAct.setIcon(
                QtGui.QIcon(os.path.join("Resources", "images", "out")))

    def loadLibrary(self):
        self.snippetsListWidget.clear()
        files = sorted(os.listdir(self.useData.appPathDict["librarydir"]))
        alpha = {}
        for i in files:
            c = list(i)[0].upper()
            if c not in alpha:
                alpha[c] = []
        for i in files:
            c = list(i)[0].upper()
            alpha[c].append(i)
        # sort top level alphabets in descending order
        alpha = sorted(alpha.items(), key=lambda member: member[0])
        self.alphaSearchBox.clear()
        for v in alpha:
            self.alphaSearchBox.addItem(v[0])
            parent = QtWidgets.QTreeWidgetItem(0)
            parent.setText(0, v[0])
            parent.setForeground(0, QtGui.QBrush(QtGui.QColor("#FF0000")))
            self.snippetsListWidget.addTopLevelItem(parent)
            for i in sorted(v[1]):
                item = QtWidgets.QTreeWidgetItem(1)
                item.setText(0, i)
                item.setToolTip(0, i)
                itemSize = os.path.getsize(os.path.join(
                    self.useData.appPathDict["librarydir"], i))
                item.setText(1, sizeformat(itemSize))
                item.setToolTip(1, "")
                parent.addChild(item)
        self.snippetsListWidget.expandAll()
        self.snippetsListWidget.resizeColumnToContents(1)

        count = len(files)
        if count == 0:
            self.removeAct.setDisabled(True)
            self.renameAct.setDisabled(True)
            self.printAct.setDisabled(True)
        else:
            self.removeAct.setDisabled(False)
            self.renameAct.setDisabled(False)
            self.printAct.setDisabled(False)
        self.libraryCountLabel.setText(str(count) + " items")

    def viewLibraryItem(self, item):
        if item.type() == 0:
            return
        self.currentSnippetItem = item
        path = os.path.join(self.useData.appPathDict[
                            "librarydir"], item.data(0, 0))
        self.showExtraData(path)

        self.currentSnippetNameLabel.setText(item.data(0, 0))

    def viewSearchItem(self, item):
        self.currentSnippetItem = item
        path = os.path.join(self.useData.appPathDict[
                            "librarydir"], item.text())
        self.showExtraData(path)

        self.currentSnippetNameLabel.setText(item.text())

    def showExtraData(self, path):
        # FIXME QtXml is no longer supported.
        dom_document = QtXml.QDomDocument()
        file = open(path, "r")
        dom_document.setContent(file.read())
        file.close()

        documentElement = dom_document.documentElement()
        childElement = documentElement.firstChild().toElement()
        source = ''  # for compatibilty with older versions of library files
        while childElement.isNull() is False:
            if childElement.nodeName() == 'comments':
                comments = childElement.firstChild().nodeValue()
            elif childElement.nodeName() == 'code':
                code = childElement.firstChild().nodeValue()
            elif childElement.nodeName() == 'source':
                source = childElement.firstChild().nodeValue()
            childElement = childElement.nextSibling()

        self.commentViewer.setPlainText(comments)
        self.codeViewer.setText(code)
        self.sourceLine.setText(source)

    def removeItem(self):
        mess = 'Remove "{0}" from library?'.format(
            self.currentSnippetItem.text(0))
        reply = QtWidgets.QMessageBox.warning(self, "Remove", mess,
                                          QtWidgets.QMessageBox.StandardButton.Yes | 
                                          QtWidgets.QMessageBox.StandardButton.No)
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            path = os.path.join(self.useData.appPathDict["librarydir"],
                                self.currentSnippetNameLabel.text())
            try:
                os.remove(path)
                self.loadLibrary()
            except:
                message = QtWidgets.QMessageBox.warning(self, "Remove",
                                                    "Failed to remove item!")

    def printFile(self):
        document = self.codeViewer.document()
        printer = QtPrintSupport.QPrinter()

        dlg = QtPrintSupport.QPrintDialog(printer, self)
        if dlg.exec_() != QtWidgets.QDialog.Accepted:
            return
        document.print_(printer)

    def rename(self):
        old_path = os.path.join(self.useData.appPathDict["librarydir"],
                                self.currentSnippetItem.text(0))
        base_dir = os.path.dirname(old_path)
        c = os.path.splitext(os.path.basename(old_path))
        head = c[0]
        extension = c[1]

        newName = GetName("Rename", self.useData.appPathDict["librarydir"],
                          head, self)
        if newName.accepted:
            text = newName.name.strip()
            new_path = os.path.join(base_dir, text + extension)
            try:
                os.rename(old_path, new_path)
                self.loadLibrary()
            except Exception as err:
                message = QtWidgets.QMessageBox.warning(self, "Rename",
                                                    "Renaming failed!\n\n{0}".format(str(err)))

    def selectAll(self):
        self.codeViewer.selectAll()

    def export(self):
        options = QtWidgets.QFileDialog.Options()
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self,
                                                         "Export Library",
                                                         os.path.join(
                                                             self.useData.getLastOpenedDir(),
                                                             "PyCoder_Library" + '_' + QtCore.QDateTime().currentDateTime().toString().replace(' ', '_').replace(':', '-') + '.pcdlib'),
                                                         "PyCoder Library (*.pcdlib);", options=options)
        if fileName:
            self.useData.saveLastOpenedDir(os.path.split(fileName)[0])
            try:
                QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
                fileName = os.path.normpath(fileName)
                shutil.make_archive(fileName, "zip",
                                    self.useData.appPathDict["librarydir"])
            except Exception as err:
                mess = str(err.args[1])
                QtWidgets.QApplication.restoreOverrideCursor()
                message = QtWidgets.QMessageBox.critical(self,
                                                         "Export Library", mess)
            QtWidgets.QApplication.restoreOverrideCursor()
        else:
            return False


    def addToLibrary(self, editorTabWidget):
        if editorTabWidget.getSource().strip() == '':
            message = QtWidgets.QMessageBox.warning(self, "Library Add",
                                                "Source code must be present to add to library!")
            return
        add = LibraryAddDialog(editorTabWidget, self)
        if add.accepted:
            path = os.path.join(self.useData.appPathDict[
                                "librarydir"], add.name)
            if os.path.exists(path):
                mess = "File already exists in Library.\n\nReplace it?"
                reply = QtWidgets.QMessageBox.warning(self, "Library Add",
                                                  mess, QtWidgets.QMessageBox.StandardButton.Yes | 
                                                  QtWidgets.QMessageBox.StandardButton.No)
                if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                    pass
                else:
                    return
            try:
                # FIXME QtXml is no longer supported.
                dom_document = QtXml.QDomDocument("snippet")
                root = dom_document.createElement("snippet")
                dom_document.appendChild(root)

                tag = dom_document.createElement('comments')
                root.appendChild(tag)

                t = dom_document.createCDATASection(
                    add.commentEntry.toPlainText())
                tag.appendChild(t)

                tag = dom_document.createElement('source')
                root.appendChild(tag)

                if add.entireModuleButton.isChecked():
                    t = dom_document.createCDATASection("Main")
                    tag.appendChild(t)
                else:
                    t = dom_document.createCDATASection(
                        editorTabWidget.getTabName())
                    tag.appendChild(t)

                tag = dom_document.createElement('code')
                root.appendChild(tag)

                if add.entireModuleButton.isChecked():
                    t = dom_document.createCDATASection(
                        editorTabWidget.getSource())
                else:
                    t = dom_document.createCDATASection(
                        editorTabWidget.focusedEditor().selectedText())
                tag.appendChild(t)

                file = open(path, "w")
                file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                file.write(dom_document.toString())
                file.close()
                self.loadLibrary()
                self.close()
            except Exception as err:
                message = QtWidgets.QMessageBox.warning(self, "Library Add",
                                                    "Adding to Library failed!\n\n{0}".format(str(err)))
