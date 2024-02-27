import sys
import os
import traceback
import logging

from PyQt6 import QtCore, QtGui, QtWidgets

# rope
from rope.refactor.rename import Rename
from rope.refactor.topackage import ModuleToPackage
from rope.refactor import inline
from rope.refactor.localtofield import LocalToField
from rope.base.project import Project
from rope.base import libutils

from rope.contrib.findit import (find_occurrences, find_implementations,
                                 find_definition)
from Extensions_Qt6.Refactor.UsageDialog import UsageDialog


class GetName(QtWidgets.QDialog):

    def __init__(self, caption, defaultText, parent=None):
        QtWidgets.QDialog.__init__(self, parent, QtCore.Qt.WindowType.Window |
                               QtCore.Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle(caption)

        mainLayout = QtWidgets.QVBoxLayout()

        mainLayout.addWidget(QtWidgets.QLabel(_("New name:")))

        self.nameLine = QtWidgets.QLineEdit()
        self.nameLine.setText(defaultText)
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

        self.resize(300, 20)
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


class FindUsageThread(QtCore.QThread):

    def run(self):
        self.error = None
        self.foundList = []
        try:
            resource = libutils.path_to_resource(self.ropeProject, self.path)
            result = find_occurrences(self.ropeProject, resource, self.offset)
            self.itemsDict = {}
            if len(result) == 0:
                self.error = _("No usages found.")
            else:
                for i in result:
                    line = i.lineno
                    path = i.resource.path
                    if path in self.itemsDict:
                        self.itemsDict[path].append(line)
                    else:
                        self.itemsDict[path] = [line]
        except Exception as err:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.error(repr(traceback.format_exception(exc_type, exc_value,
                         exc_traceback)))

            self.error = str(err)

    def find(self, path, ropeProject, offset):
        self.path = path
        self.ropeProject = ropeProject
        self.offset = offset

        self.start()


class RenameThread(QtCore.QThread):

    def run(self):
        self.error = None
        self.changedFiles = []
        try:
            self.ropeProject.validate()
            rename = Rename(self.ropeProject, libutils.path_to_resource(
                self.ropeProject, self.path), self.offset)
            changes = rename.get_changes(self.new_name)
            self.ropeProject.do(changes)
            changed = changes.get_changed_resources()
            # changed is a set
            for i in changed:
                self.changedFiles.append(i.real_path)
        except Exception as err:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.error(repr(traceback.format_exception(exc_type, exc_value,
                         exc_traceback)))
                             
            self.error = str(err)

    def rename(self, new_name, path, ropeProject, offset):
        self.new_name = new_name
        self.path = path
        self.ropeProject = ropeProject
        self.offset = offset

        self.start()


class InlineThread(QtCore.QThread):

    def run(self):
        self.error = None
        self.changedFiles = []
        try:
            inlined = inline.create_inline(
                self.ropeProject, self.resource, self.offset)
            changes = inlined.get_changes()
            self.ropeProject.do(changes)
            changed = changes.get_changed_resources()
            # changed is a set
            for i in changed:
                self.changedFiles.append(i.real_path)
        except Exception as err:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.error(repr(traceback.format_exception(exc_type, exc_value,
                         exc_traceback)))
            
            self.error = str(err)

    def inline(self, project, resource, offset):
        self.resource = resource
        self.ropeProject = project
        self.offset = offset

        self.start()


class LocalToFieldThread(QtCore.QThread):

    def run(self):
        self.error = None
        self.changedFiles = []
        try:
            convert = LocalToField(
                self.ropeProject, self.resource, self.offset)
            changes = convert.get_changes()
            self.ropeProject.do(changes)
            changed = changes.get_changed_resources()
            # changed is a set
            for i in changed:
                self.changedFiles.append(i.real_path)
        except Exception as err:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.error(repr(traceback.format_exception(exc_type, exc_value,
                         exc_traceback)))

            self.error = str(err)

    def convert(self, project, resource, offset):
        self.resource = resource
        self.ropeProject = project
        self.offset = offset

        self.start()


class ModuleToPackageThread(QtCore.QThread):

    def run(self):
        self.error = None
        try:
            convert = ModuleToPackage(self.ropeProject,
                                      libutils.path_to_resource(self.ropeProject, self.path))
            changes = convert.get_changes()
            self.ropeProject.do(changes)
        except Exception as err:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.error(repr(traceback.format_exception(exc_type, exc_value,
                         exc_traceback)))

            self.error = str(err)

    def convert(self, path, ropeProject):
        self.path = path
        self.ropeProject = ropeProject

        self.start()


class Refactor(QtWidgets.QWidget):

    def __init__(self, editorTabWidget, busyWidget, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.editorTabWidget = editorTabWidget
        self.busyWidget = busyWidget
        self.root = editorTabWidget.projectPathDict["sourcedir"]
        self.useData = editorTabWidget.useData
        ropeFolder = editorTabWidget.projectPathDict["ropeFolder"]

        libraryList = []
        for i, v in self.useData.libraryDict.items():
            libraryList.extend(v[0])
        prefs = {
            'ignored_resources': ['*.pyc', '*~', '.ropeproject',
                                  '.hg', '.svn', '_svn', '.git',
                                  '__pycache__'],
            'python_files': ['*.py', '*.pyw'],
            'save_objectdb': True,
            'compress_objectdb': False,
            'automatic_soa': True,
            'soa_followed_calls': 0,
            'perform_doa': True,
            'validate_objectdb': True,
            'max_history_items': 32,
            'save_history': True,
            'compress_history': False,
            'indent_size': 4,
            'extension_modules': libraryList,
            'import_dynload_stdmods': True,
            'ignore_syntax_errors': True,
            'ignore_bad_imports': True
            }

        self.ropeProject = Project(
            projectroot=self.root, ropefolder=ropeFolder, **prefs)

        if sys.platform.startswith('win'):
            self.ropeProject.prefs.add('python_path', 'c:/Python33')
            self.ropeProject.prefs.add('source_folders', 'c:/Python33/Lib')
        self.ropeProject.validate()

        self.noProject = Project(projectroot="temp", ropefolder=None)

        self.findThread = FindUsageThread()
        self.findThread.finished.connect(self.findOccurrencesFinished)

        self.renameThread = RenameThread()
        self.renameThread.finished.connect(self.renameFinished)

        self.inlineThread = InlineThread()
        self.inlineThread.finished.connect(self.inlineFinished)

        self.localToFieldThread = LocalToFieldThread()
        self.localToFieldThread.finished.connect(self.localToFieldFinished)

        self.moduleToPackageThread = ModuleToPackageThread()
        self.moduleToPackageThread.finished.connect(
            self.moduleToPackageFinished)

        self.createActions()

        self.refactorMenu = QtWidgets.QMenu(_("Refactor"))
        self.refactorMenu.addAction(self.renameAttributeAct)
        self.refactorMenu.addAction(self.inlineAct)
        self.refactorMenu.addAction(self.localToFieldAct)

    def closeRope(self):
        self.ropeProject.close()

    def createActions(self):
        self.findDefAct = \
            QtGui.QAction(
                QtGui.QIcon(os.path.join("Resources", "images", "map_marker")),
                _("Go-to Definition"), self, statusTip=_("Go-to where ara available definition"),
                triggered=self.findDefinition)

        self.findOccurrencesAct = \
            QtGui.QAction(_("Usages"), self, statusTip=_("Search to other usages"),
                          triggered=self.findOccurrences)

        self.moduleToPackageAct = \
            QtGui.QAction(
                _("Convert to Package"), self, statusTip=_("Convert to Package"),
                triggered=self.moduleToPackage)

        self.renameModuleAct = \
            QtGui.QAction(_("Rename"), self, statusTip=_("Rename module to..."),
                          triggered=self.renameModule)

        self.renameAttributeAct = \
            QtGui.QAction(_("Rename"), self, statusTip=_("Rename attribute to..."),
                          triggered=self.renameAttribute)

        self.inlineAct = \
            QtGui.QAction(_("Inline"), self, statusTip=_("Inline"),
                          triggered=self.inline)

        self.localToFieldAct = \
            QtGui.QAction(_("Local-to-Field"), self, statusTip=_("Local-to-Field"),
                          triggered=self.localToField)

    def renameModule(self):
        index = self.editorTabWidget.currentIndex()
        moduleName = self.editorTabWidget.tabText(index)
        moduleName = os.path.splitext(moduleName)[0]
        newName = GetName(_("Rename"), moduleName, self)
        project = self.getProject()
        if newName.accepted:
            saved = self.editorTabWidget.saveProject()
            if saved:
                path = self.editorTabWidget.getEditorData("filePath")
                self.renameThread.rename(newName.text, path, project, None)
                self.busyWidget.showBusy(True, _("Renaming... please wait!"))

    def renameAttribute(self):
        objectName = self.editorTabWidget.get_current_word()
        if objectName == '':
            self.editorTabWidget.showNotification(
                _("No word under cursor."))
            return
        newName = GetName(_("Rename"), objectName, self)
        if newName.accepted:
            project = self.getProject()
            saved = self.editorTabWidget.saveProject()
            if saved:
                offset = self.getOffset()
                path = self.editorTabWidget.getEditorData("filePath")
                self.renameThread.rename(newName.text, path, project, offset)
                self.busyWidget.showBusy(True, _("Renaming... please wait!"))

    def renameFinished(self):
        self.busyWidget.showBusy(False)
        if self.renameThread.error is not None:
            message = QtWidgets.QMessageBox.warning(self, _("Failed Rename"),
                                                self.renameThread.error)
            return
        if self.renameThread.offset is None:
            # filename has been changed
            oldPath = self.editorTabWidget.getEditorData("filePath")
            ext = os.path.splitext(oldPath)[1]
            newPath = os.path.join(os.path.dirname(oldPath),
                                   self.renameThread.new_name + ext)
            self.editorTabWidget.updateEditorData("filePath", newPath)
        else:
            if len(self.renameThread.changedFiles) > 0:
                self.editorTabWidget.reloadModules(
                    self.renameThread.changedFiles)

    def inline(self):
        offset = self.getOffset()
        path = self.editorTabWidget.getEditorData("filePath")
        project = self.getProject()
        resource = libutils.path_to_resource(project, path)
        saved = self.editorTabWidget.saveProject()
        if saved:
            self.inlineThread.inline(project, resource, offset)
            self.busyWidget.showBusy(True, _("Inlining... please wait!"))

    def inlineFinished(self):
        self.busyWidget.showBusy(False)
        if self.inlineThread.error is not None:
            message = QtWidgets.QMessageBox.warning(self, _("Failed Inline"),
                                                self.inlineThread.error)
            return
        if len(self.inlineThread.changedFiles) > 0:
            self.editorTabWidget.reloadModules(self.inlineThread.changedFiles)

    def localToField(self):
        offset = self.getOffset()
        path = self.editorTabWidget.getEditorData("filePath")
        project = self.getProject()
        resource = libutils.path_to_resource(project, path)
        saved = self.editorTabWidget.saveProject()
        if saved:
            self.localToFieldThread.convert(project, resource, offset)
            self.busyWidget.showBusy(
                True, _("Converting Local to Field... please wait!"))

    def localToFieldFinished(self):
        self.busyWidget.showBusy(False)
        if self.localToFieldThread.error is not None:
            message = QtWidgets.QMessageBox.warning(self, _("Failed Local-to-Field"),
                                                self.localToFieldThread.error)
            return
        if len(self.localToFieldThread.changedFiles) > 0:
            self.editorTabWidget.reloadModules(
                self.localToFieldThread.changedFiles)

    def findDefinition(self):
        saved = self.editorTabWidget.saveProject()
        if saved:
            offset = self.getOffset()
            path = self.editorTabWidget.getEditorData("filePath")
            project = self.getProject()
            resource = libutils.path_to_resource(project, path)
            try:
                result = find_definition(project,
                                         self.editorTabWidget.getSource(), offset, resource)
                if result is None:
                    self.editorTabWidget.showNotification(
                        _("No definition found."))
                else:
                    start, end = result.region
                    offset = result.offset
                    line = result.lineno
                    result_path = result.resource.path
                    sourcePath = self.editorTabWidget.projectPathDict[
                        "sourcedir"]
                    if not os.path.isabs(result_path):
                        result_path = os.path.join(sourcePath, result_path)
                    if os.path.samefile(result_path, path):
                        pass
                    else:
                        self.editorTabWidget.loadfile(result_path)
                    editor = self.editorTabWidget.focusedEditor()
                    start = editor.lineIndexFromPosition(start)
                    end = editor.lineIndexFromPosition(end)
                    editor.setSelection(start[0], start[1], end[0], end[1])
                    editor.ensureLineVisible(line - 1)
            except Exception as err:
                self.editorTabWidget.showNotification(str(err))

    def moduleToPackage(self):
        path = self.editorTabWidget.getEditorData("filePath")
        project = self.getProject()
        saved = self.editorTabWidget.saveProject()
        if saved:
            self.moduleToPackageThread.convert(path, project)
            self.busyWidget.showBusy(True, _("Converting... please wait!"))

    def moduleToPackageFinished(self):
        self.busyWidget.showBusy(False)
        if self.moduleToPackageThread.error is not None:
            message = QtWidgets.QMessageBox.warning(self, _("Failed to convert"),
                                                self.moduleToPackageThread.error)

    def findOccurrences(self):
        self.objectName = self.editorTabWidget.get_current_word()

        if self.objectName == '':
            self.editorTabWidget.showNotification(
                _("No word under cursor."))
            return
        offset = self.getOffset()
        project = self.getProject()
        saved = self.editorTabWidget.saveProject()
        if saved:
            path = self.editorTabWidget.getEditorData("filePath")
            self.findThread.find(path, project, offset)
            self.busyWidget.showBusy(True, _("Finding usages... please wait!"))

    def findOccurrencesFinished(self):
        self.busyWidget.showBusy(False)
        if self.findThread.error is not None:
            self.editorTabWidget.showNotification(self.findThread.error)
            return
        if len(self.findThread.itemsDict) > 0:
            foundList = []
            for parent, lines in self.findThread.itemsDict.items():
                parentItem = QtWidgets.QTreeWidgetItem()
                parentItem.setForeground(0, QtGui.QBrush(
                    QtGui.QColor("#003366")))
                parentItem.setText(0, parent)
                for line in lines:
                    childItem = QtWidgets.QTreeWidgetItem()
                    childItem.setText(0, str(line))
                    childItem.setFirstColumnSpanned(True)
                    parentItem.addChild(childItem)
                    foundList.append(parentItem)
            usageDialog = UsageDialog(
                self.editorTabWidget, _("Usages: ") + self.objectName, foundList, self)
        else:
            self.editorTabWidget.showNotification(_("No usages found."))

    def getOffset(self):
        return self.editorTabWidget.getOffset()

    def get_absolute_coordinates(self):
        editor = self.editorTabWidget.focusedEditor()
        point = editor.get_absolute_coordinates()
        return point

    def getProject(self):
        path = self.editorTabWidget.getEditorData("filePath")
        if path is None:
            return self.noProject
        if path.startswith(self.editorTabWidget.projectPathDict["sourcedir"]):
            return self.ropeProject
        else:
            return self.noProject
