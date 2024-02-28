import os
import shutil
from PyQt6 import QtCore, QtGui, QtWidgets

from Extensions_Qt6.Projects.ProjectManager.ProjectView.ProjectView import ProjectView
from Extensions_Qt6.Projects.ProjectManager.Build import Build


class ExportThread(QtCore.QThread):

    def run(self):
        self.error = None
        try:
            shutil.make_archive(self.fileName, "zip", self.path)
        except Exception as err:
            self.error = str(err)

    def export(self, fileName, path):
        self.fileName = fileName
        self.path = path

        self.start()


class ProjectManager(QtWidgets.QWidget):

    def __init__(
        self, editorTabWidget, messagesWidget, projectPathDict, projectSettings,
            useData, app,
            busyWidget, buildStatusWidget, parent):
        QtWidgets.QWidget.__init__(self, parent)

        self.busyWidget = busyWidget
        self.editorTabWidget = editorTabWidget

        self.useData = useData
        self.projects = parent
        self.projects = parent

        self.configDialog = editorTabWidget.configDialog

        if projectPathDict["type"] == _("Desktop Application") or projectPathDict["type"] == "Desktop Application":
            self.build = Build(
                buildStatusWidget, messagesWidget, projectPathDict, projectSettings, useData,
                self.configDialog.buildConfig, editorTabWidget, self)

        self.exportThread = ExportThread()
        self.exportThread.finished.connect(self.finishExport)

        self.projectView = ProjectView(
            self.editorTabWidget, projectPathDict["sourcedir"], app, projectSettings)

    def buildProject(self):
        if self.editorTabWidget.errorsInProject():
            reply = QtWidgets.QMessageBox.warning(self, _("Build"),
                                              _("There are errors in your project. Build anyway?"),
                                              QtWidgets.QMessageBox.StandardButton.Yes | 
                                              QtWidgets.QMessageBox.StandardButton.No)
            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                self.build.build()
            else:
                return
        else:
            self.build.build()

    def configureProject(self):
        self.configDialog.exec()

    def openBuild(self):
        self.build.openDir()

    def exportProject(self):
        curren_window = self.projects.projectWindowStack.currentWidget()
        name = curren_window.projectPathDict["name"]
        path = curren_window.projectPathDict["root"]

        savepath = os.path.join(self.useData.getLastOpenedDir(), name)
        savepath = os.path.normpath(savepath)
        fileName = QtWidgets.QFileDialog.getSaveFileName(self,
                                                     _("Export"), savepath,
                                                     _("All files (*)"))[0]
        if fileName:
            self.useData.saveLastOpenedDir(os.path.split(fileName)[0])

            self.exportThread.export(fileName, path)
            self.busyWidget.showBusy(True, _("Exporting project... please wait!"))

    def finishExport(self):
        self.busyWidget.showBusy(False)
        if self.exportThread.error is not None:
            message = QtWidgets.QMessageBox.warning(
                self, _("Export Failed"), self.exportThread.error)
