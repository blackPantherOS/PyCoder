import os
import sys
import shutil

# FIXME QtXml is no longer supported.
from PyQt6 import QtCore, QtGui, QtWidgets, QtXml

from Extensions_Qt6.Projects.ProjectManager.ProjectView.ProjectView import IconProvider
from venv import EnvBuilder

from Extensions_Qt6 import StyleSheet

class SelectBox(QtWidgets.QDialog):

    def __init__(self, caption, itemsList, parent=None):
        QtWidgets.QDialog.__init__(self, parent, QtCore.Qt.WindowType.Window | QtCore.Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle(caption)

        mainLayout = QtWidgets.QVBoxLayout()

        self.itemBox = QtWidgets.QComboBox()
        self.itemBox.addItem()
        for i in itemsList:
            self.itemBox.addItems(itemsList)
        self.itemBox.currentIndexChanged.connect(self.enableAcceptButton)
        mainLayout.addWidget(self.itemBox)

        hbox = QtWidgets.QHBoxLayout()

        hbox.addStretch(1)

        self.acceptButton = QtWidgets.QPushButton(_("Ok"))
        self.acceptButton.setDisabled(True)
        self.acceptButton.clicked.connect(self.accept)
        hbox.addWidget(self.acceptButton)

        self.cancelButton = QtWidgets.QPushButton(_("Cancel"))
        self.cancelButton.clicked.connect(self.cancel)
        hbox.addWidget(self.cancelButton)

        mainLayout.addLayout(hbox)

        self.setLayout(mainLayout)

        self.resize(400, 20)
        self.enableAcceptButton()

        self.exec()

    def enableAcceptButton(self):
        if self.itemBox.currentIndex() == 0:
            self.acceptButton.setDisabled(True)
        else:
            self.acceptButton.setDisabled(False)

    def accept(self):
        self.accepted = True
        self.item = self.itemBox.currentText()
        self.close()

    def cancel(self):
        self.accepted = False
        self.close()


class GetText(QtWidgets.QDialog):

    def __init__(self, caption, format, parent=None):
        QtWidgets.QDialog.__init__(self, parent, QtCore.Qt.WindowType.Window |
                               QtCore.Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle(caption)

        mainLayout = QtWidgets.QVBoxLayout()

        mainLayout.addWidget(QtWidgets.QLabel(format))

        self.nameLine = QtWidgets.QLineEdit()
        self.nameLine.selectAll()
        self.nameLine.textChanged.connect(self.enableAcceptButton)
        mainLayout.addWidget(self.nameLine)

        hbox = QtWidgets.QHBoxLayout()

        self.statusLabel = QtWidgets.QLabel()
        hbox.addWidget(self.statusLabel)

        hbox.addStretch(1)

        self.acceptButton = QtWidgets.QPushButton(_("Ok"))
        self.acceptButton.setDisabled(True)
        self.acceptButton.clicked.connect(self.accept)
        hbox.addWidget(self.acceptButton)

        self.cancelButton = QtWidgets.QPushButton(_("Cancel"))
        self.cancelButton.clicked.connect(self.cancel)
        hbox.addWidget(self.cancelButton)

        mainLayout.addLayout(hbox)

        self.setLayout(mainLayout)

        self.resize(400, 20)
        self.enableAcceptButton()

        self.exec()

    def enableAcceptButton(self):
        text = self.nameLine.text().strip()
        if text == '':
            self.acceptButton.setDisabled(True)
        else:
            self.acceptButton.setDisabled(False)

    def accept(self):
        self.accepted = True
        self.text = self.nameLine.text().strip()
        self.close()

    def cancel(self):
        self.accepted = False
        self.close()


class RopeConfig(QtWidgets.QWidget):

    def __init__(self, projectPathDict, useData, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(mainLayout)

        self.ignoreSyntaxErrorsBox = QtWidgets.QComboBox()
        self.ignoreSyntaxErrorsBox.addItem(_("Ignore Syntax Errors"))
        self.ignoreSyntaxErrorsBox.addItem(_("Don't Ignore Syntax Errors"))
#        self.ignoreSyntaxErrorsBox.setCurrentIndex(
# self.ignoreSyntaxErrorsBox.findText(profileData["appendscripttolibrary"]))
        mainLayout.addWidget(self.ignoreSyntaxErrorsBox)

        self.ignoreBadImportsBox = QtWidgets.QComboBox()
        self.ignoreBadImportsBox.addItem(_("Ignore Bad Imports"))
        self.ignoreBadImportsBox.addItem(_("Don't Ignore Bad Imports"))
#        self.ignoreBadImportsBox.setCurrentIndex(
# self.ignoreBadImportsBox.findText(profileData["appendscripttolibrary"]))
        mainLayout.addWidget(self.ignoreBadImportsBox)

        hbox = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(hbox)

        hbox.addWidget(QtWidgets.QLabel(_("Max History Items: ")))
        self.maxHistoryBox = QtWidgets.QSpinBox()
        hbox.addWidget(self.maxHistoryBox)

        frame = QtWidgets.QFrame()
        frame.setGeometry(1, 1, 1, 2)
        frame.setFrameShape(frame.Shape.HLine)
        frame.setFrameShadow(frame.Shadow.Sunken)
        mainLayout.addWidget(frame)

        self.listSelectorBox = QtWidgets.QComboBox()
        self.listSelectorBox.addItem(_("Extensions_Qt6"))
        self.listSelectorBox.addItem(_("Ignored Resources"))
        self.listSelectorBox.addItem(_("Custom Folders"))
#        self.listSelectorBox.activated.connect(self.viewList)
#        self.listSelectorBox.currentIndexChanged.connect(self.viewList)
        mainLayout.addWidget(self.listSelectorBox)

        self.listWidget = QtWidgets.QListWidget()
        mainLayout.addWidget(self.listWidget)

        self.helpDict = {
            _("Extensions_Qt6"): _("Specify which files should be considered python files."),
            _("Ignored Resources"): _("Specify which files and folders to ignore in the project."),
            _("Custom Folders"): (
                _("By default rope searches the project for finding source folders\n"
                "(folders that should be searched for finding modules).\n"
                "You can add paths to that list. Note that rope guesses project \n"
                "source folders correctly most of the time; use this if you have \n"
                "any problems.\n"
                "The folders should be relative to project root and use '/' for\n"
                "separating folders regardless of the platform rope is running on.\n"
                "src/my_source_folder' for instance.")
                )
            }

        self.docLabel = QtWidgets.QLabel()
        self.docLabel.setWordWrap(True)
        mainLayout.addWidget(self.docLabel)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        mainLayout.addLayout(hbox)

        self.addButton = QtWidgets.QPushButton()
        self.addButton.setIcon(
            QtGui.QIcon(os.path.join("Resources", "images", "add")))
#        self.addButton.clicked.connect(self.appendToList)
        hbox.addWidget(self.addButton)

        self.removeButton = QtWidgets.QPushButton()
        self.removeButton.setIcon(
            QtGui.QIcon(os.path.join("Resources", "images", "minus")))
#        self.removeButton.clicked.connect(self.removeItem)
        hbox.addWidget(self.removeButton)

        hbox.addStretch(1)

    def save(self):
        fileName = self.projectPathDict["ropeprofile"]

        # FIXME QtXml is no longer supported.
        dom_document = QtXml.QDomDocument("rope_profile")

        main_data = dom_document.createElement("rope")
        dom_document.appendChild(main_data)

        root = dom_document.createElement("ignoresyntaxerrors")
        attrib = dom_document.createTextNode(
            self.ignoreSyntaxErrorsBox.currentText())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("ignorebadimports")
        attrib = dom_document.createTextNode(
            self.ignoreBadImportsBox.currentText())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("maxhistoryitems")
        attrib = dom_document.createTextNode(str(self.maxHistoryBox.value()))
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("Extensions_Qt6")
        main_data.appendChild(root)

        defExt = ['*.py', '*.pyw']
        for i in defExt:
            tag = dom_document.createElement("item")
            root.appendChild(tag)

            t = dom_document.createTextNode(i)
            tag.appendChild(t)

        root = dom_document.createElement("IgnoredResources")
        main_data.appendChild(root)

        defIgnore = ["*.pyc", "*~", ".ropeproject",
                     ".hg", ".svn", "_svn", ".git", "__pycache__"]
        for i in defIgnore:
            tag = dom_document.createElement("item")
            root.appendChild(tag)

            t = dom_document.createTextNode(i)
            tag.appendChild(t)

        root = dom_document.createElement("CustomFolders")
        main_data.appendChild(root)

        file = open(fileName, "w")
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write(dom_document.toString())
        file.close()


class VenvSetup(QtWidgets.QWidget):

    def __init__(self, projectPathDict, projectSettings, useData, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.projectPathDict = projectPathDict
        self.useData = useData
        self.projectSettings = projectSettings

        mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(mainLayout)

        hbox = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(hbox)

        hbox.addWidget(QtWidgets.QLabel(_("Version: ")))

        self.currentVersionLabel = QtWidgets.QLabel()
        hbox.addWidget(self.currentVersionLabel)

        self.openButton = QtWidgets.QPushButton(_("Open"))
        self.openButton.clicked.connect(self.openVenv)
        hbox.addWidget(self.openButton)

        hbox.setStretch(1, 1)

        self.treeView = QtWidgets.QTreeView()

        self.iconProvider = IconProvider()

        self.treeView.setModel(self.newFileSystemModel())
        self.treeView.setColumnWidth(0, 300)
        mainLayout.addWidget(self.treeView)

        self.packagesPath = os.path.join(
            self.projectPathDict["venvdir"], "Lib", "site-packages")
        if os.path.exists(self.projectPathDict["venvdir"]):
            self.currentVersionLabel.setText(self.setVesionFromVenv())
            self.treeView.setRootIndex(
                self.treeView.model().index(self.packagesPath))

        hbox = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(hbox)

        self.installVenvButton = QtWidgets.QPushButton("Install")
        self.installVenvButton.clicked.connect(self.install)
        hbox.addWidget(self.installVenvButton)

        self.upgradeVenvButton = QtWidgets.QPushButton("Upgrade")
        self.upgradeVenvButton.clicked.connect(self.upgrade)
        hbox.addWidget(self.upgradeVenvButton)

        self.uninstallVenvButton = QtWidgets.QPushButton("Uninstall")
        self.uninstallVenvButton.clicked.connect(self.uninstall)
        hbox.addWidget(self.uninstallVenvButton)

    def openVenv(self):
        if os.path.exists(self.projectPathDict["venvdir"]):
            os.startfile(self.projectPathDict["venvdir"])

    def setVesionFromVenv(self):
        path = os.path.join(self.projectPathDict["venvdir"], 'pyvenv.cfg')
        tempList = []
        file = open(path, 'r')
        for i in file.readlines():
            v = i.strip()
            if v == '':
                pass
            else:
                tempList.append(tuple(v.split(' = ')))
        file.close()
        settings = dict(tempList)
        return settings['version']

    def newFileSystemModel(self):
        fileSystemModel = QtGui.QFileSystemModel()
        fileSystemModel.setRootPath(QtCore.QDir.rootPath())
        fileSystemModel.setNameFilterDisables(False)
        fileSystemModel.setIconProvider(self.iconProvider)

        return fileSystemModel

    def install(self):
        if os.path.exists(self.projectPathDict["venvdir"]):
            message = QtWidgets.QMessageBox.information(
                self, "Install", "Virtual environment already installed.")
            return
        reply = QtWidgets.QMessageBox.warning(self, _("Install"),
                                         _("This will install a new virtual environment.\n\nProceed?"),
                                         QtWidgets.QMessageBox.StandardButton.Yes | 
                                         QtWidgets.QMessageBox.StandardButton.No)
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            if len(self.useData.SETTINGS["InstalledInterpreters"]) == 0:
                message = QtWidgets.QMessageBox.information(
                    self, _("Install"), _("There is no Python installation to install against.\n\nPlease make sure Python is installed."))
                return
            if len(self.useData.SETTINGS["InstalledInterpreters"]) == 1:
                pythonPath = self.useData.SETTINGS["InstalledInterpreters"][0]
            else:
                pythonPath = SelectBox(
                    _("Choose Python installation"), self.useData.SETTINGS["InstalledInterpreters"], self)
                if pythonPath.accepted:
                    pythonPath = pythonPath.item
                else:
                    return
            try:
                builder = EnvBuilder(pythonPath)
                builder.create(self.projectPathDict["venvdir"])
                self.treeView.setModel(self.newFileSystemModel())
                self.treeView.setRootIndex(
                    self.treeView.model().index(self.packagesPath))
                self.currentVersionLabel.setText(self.setVesionFromVenv())

                message = QtWidgets.QMessageBox.information(
                    self, _("Install"), _("Install virtual environment completed."))
            except Exception as err:
                message = QtWidgets.QMessageBox.warning(
                    self, _("Failed Install"), str(err))
        else:
            return

    def upgrade(self):
        if not os.path.exists(self.projectPathDict["venvdir"]):
            message = QtWidgets.QMessageBox.information(
                self, _("Install"), _("No virtual environment to upgrade."))
            return
        reply = QtWidgets.QMessageBox.warning(self, _("Install"),
                                         _("This will upgrade the current the virtual environment.\n\nProceed?"),
                                         QtWidgets.QMessageBox.StandardButton.Yes | 
                                         QtWidgets.QMessageBox.StandardButton.No)
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            if len(self.useData.SETTINGS["InstalledInterpreters"]) == 0:
                message = QtWidgets.QMessageBox.information(
                    self, _("Install"), _("There is no Python installation to install against.\n\nPlease make sure Python is installed."))
                return
            if len(self.useData.SETTINGS["InstalledInterpreters"]) == 1:
                pythonPath = self.useData.SETTINGS["InstalledInterpreters"][0]
            else:
                pythonPath = SelectBox(
                    _("Choose Python installation"), self.useData.SETTINGS["InstalledInterpreters"], self)
                if pythonPath.accepted:
                    pythonPath = pythonPath.item
                else:
                    return
            try:
                builder = EnvBuilder(pythonPath, upgrade=True)
                builder.create(self.projectPathDict["venvdir"])
                self.treeView.setModel(self.newFileSystemModel())
                self.treeView.setRootIndex(
                    self.treeView.model().index(self.packagesPath))
                self.currentVersionLabel.setText(self.setVesionFromVenv())
                message = QtWidgets.QMessageBox.information(
                    self, _("Upgrade"), _("Upgrade virtual environment completed."))
            except Exception as err:
                message = QtWidgets.QMessageBox.warning(
                    self, _("Failed Upgrade"), str(err))
        else:
            return

    def uninstall(self):
        if not os.path.exists(self.projectPathDict["venvdir"]):
            message = QtWidgets.QMessageBox.information(
                self, _("Uninstall"), _("No virtual environment to uninstall."))
            return
        reply = QtWidgets.QMessageBox.warning(self, _("Uninstall"),
                                         _("This will uninstall the current virtual environment.\n\nProceed?"),
                                         QtWidgets.QMessageBox.StandardButton.Yes | 
                                         QtWidgets.QMessageBox.StandardButton.No)
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            try:
                self.treeView.setModel(self.newFileSystemModel())
                if os.path.exists(self.projectPathDict["venvdir"]):
                    shutil.rmtree(self.projectPathDict["venvdir"])
                self.currentVersionLabel.clear()
                message = QtWidgets.QMessageBox.information(
                    self, _("Uninstall"), _("Uninstall virtual environment completed."))
            except Exception as err:
                message = QtWidgets.QMessageBox.warning(
                    self, _("Failed Uninstall"), str(err))
        else:
            return


class BuildConfig(QtWidgets.QWidget):

    def __init__(self, projectPathDict, useData, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.projectPathDict = projectPathDict
        self.useData = useData
        
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setContentsMargins(0,0, 0, 0)
        #Disabled embed contetnt size self.setMinimumWidth(400)
        self.setLayout(mainLayout)

        self.lists = {"Includes": [],
                      "Excludes": [],
                      "Constants Modules": [],
                      "Packages": [],
                      "Replace Paths": [],
                      "Bin Includes": [],
                      "Bin Excludes": [],
                      "Bin Path Includes": [],
                      "Bin Path Excludes": [],
                      "Zip Includes": [],
                      "Include Files": [],
                      "Namespace Packages": []}

        self.profileData = self.load()
        
        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.setObjectName("buildTab")
        mainLayout.addWidget(self.tabWidget)

        versionWidget = QtWidgets.QWidget()
        self.tabWidget.addTab(versionWidget,
                        QtGui.QIcon(os.path.join("Resources", "images", "arrow-045")),
                            "Version Information")

        versionLayout = QtWidgets.QFormLayout()
        versionWidget.setLayout(versionLayout)

        self.itemLine = QtWidgets.QLineEdit()
        self.itemLine.setText(self.profileData["name"])
        versionLayout.addRow(_("Name"), self.itemLine)

        self.authorLine = QtWidgets.QLineEdit()
        self.authorLine.setText(self.profileData["author"])
        versionLayout.addRow(_("Author"), self.authorLine)

        self.versionLine = QtWidgets.QLineEdit()
        self.versionLine.setText(self.profileData["version"])
        versionLayout.addRow(_("Version"), self.versionLine)

        self.descriptionLine = QtWidgets.QLineEdit()
        self.descriptionLine.setText(self.profileData["description"])
        versionLayout.addRow(_("Description"), self.descriptionLine)

        self.commentsLine = QtWidgets.QLineEdit()
        self.commentsLine.setText(self.profileData["comments"])
        versionLayout.addRow(_("Comments"), self.commentsLine)

        self.companyLine = QtWidgets.QLineEdit()
        self.companyLine.setText(self.profileData["company"])
        versionLayout.addRow(_("Company"), self.companyLine)

        self.copyrightLine = QtWidgets.QLineEdit()
        self.copyrightLine.setText(self.profileData["copyright"])
        versionLayout.addRow(_("Copyright"), self.copyrightLine)

        self.trademarksLine = QtWidgets.QLineEdit()
        versionLayout.addRow(_("Trademarks"), self.trademarksLine)

        self.productLine = QtWidgets.QLineEdit()
        self.productLine.setText(self.profileData["product"])
        versionLayout.addRow(_("Product"), self.productLine)

        #-------------------------------------------------------------------

        optionsWidget = QtWidgets.QWidget()
        self.tabWidget.addTab(optionsWidget, QtGui.QIcon(
            os.path.join("Resources", "images", "arrow-045")), _("Options"))

        optionsLayout = QtWidgets.QFormLayout()
        optionsWidget.setLayout(optionsLayout)

        self.optimizeBox = QtWidgets.QComboBox()
        self.optimizeBox.addItem(_("Don't Optimize"))
        self.optimizeBox.addItem(_("Optimize"))
        self.optimizeBox.addItem(_("Optimize (Remove Doc Strings)"))
        self.optimizeBox.setCurrentIndex(
            self.optimizeBox.findText(self.profileData["optimize"]))
        optionsLayout.addRow('', self.optimizeBox)

        self.compressBox = QtWidgets.QComboBox()
        self.compressBox.addItem(_("Compress"))
        self.compressBox.addItem(_("Don't Compress"))
        optionsLayout.addRow('',  self.compressBox)

        self.copyDepsBox = QtWidgets.QComboBox()
        self.copyDepsBox.addItem(_("Copy Dependencies"))
        self.copyDepsBox.addItem(_("Don't Copy Dependencies"))
        self.copyDepsBox.setCurrentIndex(
            self.copyDepsBox.findText(self.profileData["copydeps"]))
        optionsLayout.addRow('', self.copyDepsBox)

        self.appendScriptToExeBox = QtWidgets.QComboBox()
        self.appendScriptToExeBox.addItem(_("Append Script to Exe"))
        self.appendScriptToExeBox.addItem(_("Don't Append Script to Exe"))
        self.appendScriptToExeBox.setCurrentIndex(
            self.appendScriptToExeBox.findText(self.profileData["appendscripttoexe"]))
        optionsLayout.addRow('', self.appendScriptToExeBox)

        self.appendScriptToLibraryBox = QtWidgets.QComboBox()
        self.appendScriptToLibraryBox.addItem(_("Append Script to Library"))
        self.appendScriptToLibraryBox.addItem(_("Don't Append Script to Library"))
        self.appendScriptToLibraryBox.setCurrentIndex(
            self.appendScriptToLibraryBox.findText(self.profileData["appendscripttolibrary"]))
        optionsLayout.addRow('', self.appendScriptToLibraryBox)

        self.windowTypeBox = QtWidgets.QComboBox()
        self.windowTypeBox.addItem(_("GUI"))
        self.windowTypeBox.addItem(_("Console"))
        if self.profileData["base"] == "Win32GUI.exe":
            self.windowTypeBox.setCurrentIndex(0)
        elif self.profileData["base"] == "Console.exe":
            self.windowTypeBox.setCurrentIndex(1)
        optionsLayout.addRow(_("Window Type"), self.windowTypeBox)

        hbox = QtWidgets.QHBoxLayout()
        self.iconBox = QtWidgets.QComboBox()
        self.updateIconBox()
        f = self.iconBox.findText(self.profileData["icon"])
        if f != -1:
            self.iconBox.setCurrentIndex(f)
        hbox.addWidget(self.iconBox)

        self.addButton = QtWidgets.QToolButton()
        self.addButton.setAutoRaise(True)
        self.addButton.setToolTip(_("Add"))
        self.addButton.setIcon(
            QtGui.QIcon(os.path.join("Resources", "images", "add")))
        self.addButton.clicked.connect(self.addIcon)
        hbox.addWidget(self.addButton)

        self.removeButton = QtWidgets.QToolButton()
        self.removeButton.setAutoRaise(True)
        self.removeButton.setToolTip(_("Remove"))
        self.removeButton.setIcon(
            QtGui.QIcon(os.path.join("Resources", "images", "minus")))
        self.removeButton.clicked.connect(self.removeIcon)
        hbox.addWidget(self.removeButton)

        optionsLayout.addRow(_("Icon"), hbox)

        #-------------------------------------------------------------------

        advancedWidget = QtWidgets.QWidget()
        self.tabWidget.addTab(advancedWidget, QtGui.QIcon(
            os.path.join("Resources", "images", "arrow-045")), _("Advanced"))

        advancedLayout = QtWidgets.QVBoxLayout()
        advancedWidget.setLayout(advancedLayout)

        self.listSelectorBox = QtWidgets.QComboBox()
        for i in self.lists:
            self.listSelectorBox.addItem(i)
        self.listSelectorBox.activated.connect(self.viewList)
        self.listSelectorBox.currentIndexChanged.connect(self.viewList)
        advancedLayout.addWidget(self.listSelectorBox)

        self.listWidget = QtWidgets.QListWidget()
        advancedLayout.addWidget(self.listWidget)

        self.helpDict = {
            _("Includes"): _("List of modules to include"),
            _("Excludes"): _("List of modules to exclude"),
            _("Constants Modules"): _("List of constants to include"),
            _("Packages"): _("List of packages to include"),
            _("Replace Paths"): (
                _("Replace all the paths in modules found in the given paths "
                "with the given replacement string; each value "
                "is of the form path=replacement_string; path can be * "
                "which means all paths not already specified")),
            _("Include Files"): _("List of files to include"),
            _("Zip Includes"): (
                _("Name of file to add to the zip file or a specification of "
                "the form name=arcname which will specify the archive name "
                "to use")),
            _("Namespace Packages"): _("List of packages to include"),
            _("Bin Includes"): (
                _("Libraries that need not be included because"
                "they would normally be expected to be found on the target system or"
                "because they are part of a package which requires independent"
                "installation anyway.")),
            _("Bin Excludes"): (
                _("File names of libraries which must be included for the"
                "frozen executable to work.")),
            _("Bin Path Includes"): (
                _("Paths of directories which contain files that should "
                "be included.")),
            _("Bin Path Excludes"): (
                _("Paths of directories which contain files that should not"
                "be included, generally because they contain standard system libraries.")),
            }

        hbox = QtWidgets.QHBoxLayout()
        advancedLayout.addLayout(hbox)

        self.itemLine = QtWidgets.QLineEdit()
        self.itemLine.selectAll()
        self.itemLine.textChanged.connect(self.enableAddButton)
        hbox.addWidget(self.itemLine)

        self.addButton = QtWidgets.QPushButton()
        self.addButton.setIcon(
            QtGui.QIcon(os.path.join("Resources", "images", "add")))
        self.addButton.clicked.connect(self.appendToList)
        hbox.addWidget(self.addButton)

        self.removeButton = QtWidgets.QPushButton()
        self.removeButton.setIcon(
            QtGui.QIcon(os.path.join("Resources", "images", "minus")))
        self.removeButton.clicked.connect(self.removeItem)
        hbox.addWidget(self.removeButton)
        self.enableAddButton()

        self.docLabel = QtWidgets.QLabel()
        self.docLabel.setWordWrap(True)
        advancedLayout.addWidget(self.docLabel)

        self.viewList()
        
        hbox = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(hbox)

        self.saveButton = QtWidgets.QPushButton("Save")
        self.saveButton.clicked.connect(self.save)
        hbox.addWidget(self.saveButton)

    def updateIconBox(self):
        self.iconBox.clear()
        for i in os.listdir(self.projectPathDict['iconsdir']):
            path = os.path.join(self.projectPathDict['iconsdir'], i)
            self.iconBox.addItem(QtGui.QIcon(path), i)

    def enableAddButton(self):
        text = self.itemLine.text().strip()
        if text == '':
            self.addButton.setDisabled(True)
        elif text in self.lists[self.listSelectorBox.currentText()]:
            self.addButton.setDisabled(True)
        else:
            self.addButton.setDisabled(False)

    def viewList(self):
        self.docLabel.setText(self.helpDict[
                              self.listSelectorBox.currentText()])
        self.listWidget.clear()
        for i in self.lists[self.listSelectorBox.currentText()]:
            self.listWidget.addItem(QtWidgets.QListWidgetItem(i))

    def updateList(self):
        itemsList = []
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            itemsList.append(item.text())
        self.lists[self.listSelectorBox.currentText()] = itemsList

    def appendToList(self):
        item = self.itemLine.text()
        self.listWidget.addItem(QtWidgets.QListWidgetItem(item))
        self.updateList()
        self.enableAddButton()

    def removeItem(self):
        self.listWidget.takeItem(self.listWidget.currentRow())
        self.updateList()
        self.enableAddButton()

    def addIcon(self):
        options = QtWidgets.QFileDialog.Options()
        if sys.platform == "win32":
            file_filter = _("Icon Files (*.ico)")
        elif sys.platform == "darwin":
            file_filter = _("Icon Files (*.icns)")
        else:
            file_filter = _("Icon Files (*.png *.svg);;All Files (*)")
        filePath, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                    _("Select Icon"), self.useData.getLastOpenedDir(),
                                                    file_filter, options=options)
        if filePath:
            destPath = os.path.join(self.projectPathDict['iconsdir'],
                                    os.path.basename(filePath))
            if os.path.exists(destPath):
                reply = QtWidgets.QMessageBox.warning(self, _("Add Icon"),
                                                     _("Icon with the same name already exists. Replace?"),
                                                     QtWidgets.QMessageBox.StandardButton.Yes | 
                                                     QtWidgets.QMessageBox.StandardButton.No)
                if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                    pass
                else:
                    return
            shutil.copyfile(filePath, destPath)
            self.updateIconBox()
            f = self.iconBox.findText(os.path.basename(filePath))
            if f != -1:
                self.iconBox.setCurrentIndex(f)
            self.useData.saveLastOpenedDir(os.path.dirname(filePath))

    def removeIcon(self):
        currentIcon = self.iconBox.currentText()
        if currentIcon != '':
            path = os.path.join(self.projectPathDict['iconsdir'], currentIcon)
            if os.path.exists(path):
                try:
                    os.remove(path)
                    self.updateIconBox()
                except Exception as err:
                    message = QtWidgets.QMessageBox.warning(
                        self, _("Failed Remove"), str(err))

    def save(self):
        fileName = self.projectPathDict["buildprofile"]

        # FIXME QtXml is no longer supported.
        dom_document = QtXml.QDomDocument("build_profile")

        main_data = dom_document.createElement("build")
        dom_document.appendChild(main_data)

        root = dom_document.createElement("name")
        attrib = dom_document.createTextNode(self.itemLine.text().strip())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("author")
        attrib = dom_document.createTextNode(self.authorLine.text().strip())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("version")
        attrib = dom_document.createTextNode(self.versionLine.text().strip())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("comments")
        attrib = dom_document.createTextNode(self.commentsLine.text().strip())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("description")
        attrib = dom_document.createTextNode(
            self.descriptionLine.text().strip())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("company")
        attrib = dom_document.createTextNode(self.companyLine.text().strip())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("copyright")
        attrib = dom_document.createTextNode(self.copyrightLine.text().strip())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("trademarks")
        attrib = dom_document.createTextNode(
            self.trademarksLine.text().strip())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("product")
        attrib = dom_document.createTextNode(self.productLine.text().strip())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("base")
        attrib = dom_document.createTextNode(self.windowTypeBox.currentText())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("icon")
        attrib = dom_document.createTextNode(self.iconBox.currentText())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("compress")
        attrib = dom_document.createTextNode(self.compressBox.currentText())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("optimize")
        attrib = dom_document.createTextNode(self.optimizeBox.currentText())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("copydeps")
        attrib = dom_document.createTextNode(self.copyDepsBox.currentText())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("appendscripttoexe")
        attrib = dom_document.createTextNode(
            self.appendScriptToExeBox.currentText())
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("appendscripttolibrary")
        attrib = dom_document.createTextNode(
            self.appendScriptToLibraryBox.currentText())
        root.appendChild(attrib)
        main_data.appendChild(root)

        for key, value in self.lists.items():
            root = dom_document.createElement(key.replace(' ', '-'))
            main_data.appendChild(root)
            for i in value:
                tag = dom_document.createElement("item")
                root.appendChild(tag)

                t = dom_document.createTextNode(i)
                tag.appendChild(t)

        try:
            file = open(fileName, "w")
            file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            file.write(dom_document.toString())
            file.close()
        except:
            message = QtWidgets.QMessageBox.warning(
                self, _("Save Profile"), _("Saving failed!"))

    def load(self):
        # FIXME QtXml is no longer supported.
        dom_document = QtXml.QDomDocument()
        file = open(self.projectPathDict["buildprofile"], "r")
        dom_document.setContent(file.read())
        file.close()

        dataDict = {}

        elements = dom_document.documentElement()
        node = elements.firstChild()
        while node.isNull() is False:
            name = node.nodeName()
            expandedName = name.replace('-', ' ')
            if expandedName in self.lists:
                sub_node = node.firstChild()
                while sub_node.isNull() is False:
                    sub_prop = sub_node.toElement()
                    self.lists[expandedName].append(sub_prop.text())
                    sub_node = sub_node.nextSibling()
                dataDict[expandedName] = self.lists[expandedName]
            else:
                sub_prop = node.toElement()
                dataDict[name] = sub_prop.text()
            node = node.nextSibling()
        return dataDict


class ConfigureProject(QtWidgets.QLabel):

    def __init__(self, projectPathDict, projectSettings, useData, parent=None):
        QtWidgets.QLabel.__init__(self, parent)

        #vector self.setBackgroundRole(QtGui.QPalette.Window)
        self.setAutoFillBackground(True)
        self.setObjectName("containerLabel")
        self.setStyleSheet(StyleSheet.toolWidgetStyle)

        self.setMinimumSize(550, 450)
        self.pagesList = []

        mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(mainLayout)
        
        hbox = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(hbox)

        label = QtWidgets.QLabel(_("Project Configuration"))
        label.setObjectName("toolWidgetNameLabel")
        hbox.addWidget(label)
        
        hbox.addStretch(1)
        
        self.hideButton = QtWidgets.QToolButton()
        self.hideButton.setAutoRaise(True)
        self.hideButton.setIcon(
            QtGui.QIcon(os.path.join("Resources", "images", "cross_")))
        self.hideButton.clicked.connect(self.hide)
        hbox.addWidget(self.hideButton)

        self.tabWidget = QtWidgets.QTabWidget()

        if projectPathDict["type"] == _("Desktop Application"):
            self.buildConfig = BuildConfig(projectPathDict, useData)
            self.tabWidget.addTab(self.buildConfig,
                                  QtGui.QIcon(os.path.join("Resources", "images", "build")), _("Build"))

        self.venvSetup = VenvSetup(projectPathDict, projectSettings, useData)
        self.tabWidget.addTab(self.venvSetup,
                                  QtGui.QIcon(os.path.join("Resources", "images", "script_grey")), _("Virtual Environment"))

        self.refactorConfig = RopeConfig(projectPathDict, useData)
        # self.tabWidget.addTab(self.refactorConfig,
                              # QtGui.QIcon(os.path.join("Resources", "images", "erase"), _("Refactor"))
#        self.pagesList.append(self.libraries)

        mainLayout.addWidget(self.tabWidget)
