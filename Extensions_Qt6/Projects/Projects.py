"""
Manages all opened projects such as the creation and closing of projects
"""

import os
import sys
import shutil
import traceback
import logging
# FIXME QtXml is no longer supported.
from PyQt6 import QtCore, QtGui, QtWidgets, QtXml

from Extensions_Qt6.EditorWindow.EditorWindow import EditorWindow
from Extensions_Qt6.Projects.NewProjectDialog import NewProjectDialog


class CreateProjectThread(QtCore.QThread):

    def run(self):
        self.error = False
        try:
            self.projectPath = os.path.join(self.projDataDict["location"],
                                            self.projDataDict["name"])
            os.mkdir(self.projectPath)

            data = os.path.join(self.projectPath, "Data")
            os.mkdir(data)
            file = open(os.path.join(data, "wpad.txt"), "w")
            file.close()

            ropeFolder = os.path.join(self.projectPath, "Rope")
            print("Rope:",ropeFolder )
            os.mkdir(ropeFolder)
            shutil.copy(os.path.join("Resources", "default_config.py"),
                        os.path.join(ropeFolder, "config.py"))

            os.mkdir(os.path.join(self.projectPath, "Resources"))
            os.mkdir(os.path.join(self.projectPath, "Resources", "VirtualEnv"))
            os.mkdir(
                os.path.join(self.projectPath, "Resources", "VirtualEnv", "Linux"))
            os.mkdir(
                os.path.join(self.projectPath, "Resources", "VirtualEnv", "Mac"))
            os.mkdir(
                os.path.join(self.projectPath, "Resources", "VirtualEnv", "Windows"))
            os.mkdir(os.path.join(self.projectPath, "Resources", "Icons"))

            os.mkdir(os.path.join(self.projectPath, "temp"))
            os.mkdir(os.path.join(self.projectPath, "temp", "Backup"))
            os.mkdir(os.path.join(self.projectPath, "temp", "Backup", "Files"))

            sourceDir = os.path.join(self.projectPath, "src")
            if self.projDataDict["importdir"] != '':
                shutil.copytree(self.projDataDict["importdir"], sourceDir)
            else:
                os.mkdir(os.path.join(self.projectPath, "src"))

            if self.projDataDict["type"] == _("Desktop Application") or self.projDataDict["type"] == "Desktop Application":
                build = os.path.join(self.projectPath, "Build")
                os.mkdir(build)
                os.mkdir(os.path.join(build, "Linux"))
                os.mkdir(os.path.join(build, "Mac"))
                os.mkdir(os.path.join(build, "Windows"))

            self.mainScript = os.path.join(self.projectPath, "src",
                                           self.projDataDict["mainscript"])
            file = open(self.mainScript, 'w')
            file.close()

            if self.projDataDict["type"] == _("Desktop Application") or self.projDataDict["type"] == "Desktop Application":
                self.writeBuildProfile()
            self.writeDefaultSession()
            self.writeProjectData()
            self.writeRopeProfile()
        except Exception as err:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.error(repr(traceback.format_exception(exc_type, exc_value,
                         exc_traceback)))
            self.error = str(err)

    def writeProjectData(self):
        # FIXME QtXml is no longer supported.
        dom_document = QtXml.QDomDocument("Project")

        properties = dom_document.createElement("properties")
        dom_document.appendChild(properties)

        tag = dom_document.createElement("pycoder_project")

        tag.setAttribute("Version", "0.1")
        tag.setAttribute("Name", self.projDataDict["name"])
        tag.setAttribute("Type", self.projDataDict["type"])
        tag.setAttribute("MainScript", self.projDataDict["mainscript"])

        properties.appendChild(tag)

        file = open(os.path.join(self.projectPath, "project.xml"), "w")
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write(dom_document.toString())
        file.close()

        # FIXME QtXml is no longer supported.
        domDocument = QtXml.QDomDocument("projectdata")

        projectdata = domDocument.createElement("projectdata")
        domDocument.appendChild(projectdata)

        root = domDocument.createElement("shortcuts")
        projectdata.appendChild(root)

        root = domDocument.createElement("recentfiles")
        projectdata.appendChild(root)

        root = domDocument.createElement("favourites")
        projectdata.appendChild(root)

        root = domDocument.createElement("settings")
        projectdata.appendChild(root)

        s = 0
        defaults = {

            'ClearOutputWindowOnRun': 'False',
            'LastOpenedPath': '',
            'RunType': _('Run'),
            'BufferSize': '900',
            'RunArguments': '',
            'DefaultInterpreter': 'python3',
            'TraceType': '3',
            'RunWithArguments': 'False',
            'RunInternal': 'True',
            'UseVirtualEnv': 'False',
            'Closed': 'True',
            'Icon': '',
            'ShowAllFiles': 'True',
            'LastCloseSuccessful': 'True'
            }
        for key, value in defaults.items():
            tag = domDocument.createElement("key")
            root.appendChild(tag)

            t = domDocument.createTextNode(key + '=' + value)
            tag.appendChild(t)
            s += 1

        path = os.path.join(self.projectPath, "Data", "projectdata.xml")
        file = open(path, "w")
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write(domDocument.toString())
        file.close()

    def writeDefaultSession(self):
        # FIXME QtXml is no longer supported.
        dom_document = QtXml.QDomDocument("session")

        session = dom_document.createElement("session")
        dom_document.appendChild(session)

        file = open(os.path.join(self.projectPath, "Data", "session.xml"), "w")
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write(dom_document.toString())
        file.close()

    def writeRopeProfile(self):
        # FIXME QtXml is no longer supported.
        dom_document = QtXml.QDomDocument("rope_profile")

        main_data = dom_document.createElement("rope")
        dom_document.appendChild(main_data)

        root = dom_document.createElement("ignoresyntaxerrors")
        attrib = dom_document.createTextNode('')
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("ignorebadimports")
        attrib = dom_document.createTextNode('')
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("maxhistoryitems")
        attrib = dom_document.createTextNode('32')
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

        file = open(os.path.join(self.projectPath, "Rope", "profile.xml"), "w")
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write(dom_document.toString())
        file.close()

    def writeBuildProfile(self):
        # FIXME QtXml is no longer supported.
        dom_document = QtXml.QDomDocument("build_profile")

        main_data = dom_document.createElement("build")
        dom_document.appendChild(main_data)

        root = dom_document.createElement("name")
        attrib = dom_document.createTextNode('')
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("author")
        attrib = dom_document.createTextNode('')
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("version")
        attrib = dom_document.createTextNode('0.1')
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("comments")
        attrib = dom_document.createTextNode('')
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("description")
        attrib = dom_document.createTextNode('')
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("company")
        attrib = dom_document.createTextNode('')
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("copyright")
        attrib = dom_document.createTextNode('')
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("trademarks")
        attrib = dom_document.createTextNode('')
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("product")
        attrib = dom_document.createTextNode('')
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("base")
        attrib = dom_document.createTextNode(self.projDataDict["windowtype"])
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("icon")
        attrib = dom_document.createTextNode('')
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("compress")
        attrib = dom_document.createTextNode("Compress")
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("optimize")
        attrib = dom_document.createTextNode("Optimize")
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("copydeps")
        attrib = dom_document.createTextNode("Copy Dependencies")
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("appendscripttoexe")
        attrib = dom_document.createTextNode("Append Script to Exe")
        root.appendChild(attrib)
        main_data.appendChild(root)

        root = dom_document.createElement("appendscripttolibrary")
        attrib = dom_document.createTextNode("Append Script to Library")
        root.appendChild(attrib)
        main_data.appendChild(root)

        lists = ["Includes",
                 "Excludes",
                 "Constants Modules",
                 "Packages",
                 "Replace Paths",
                 "Bin Includes",
                 "Bin Excludes",
                 "Bin Path Includes",
                 "Bin Path Excludes",
                 "Zip Includes",
                 "Include Files",
                 "Namespace Packages"]

        for i in lists:
            root = dom_document.createElement(i.replace(' ', '-'))
            main_data.appendChild(root)

        file = open(
            os.path.join(self.projectPath, "Build", "profile.xml"), "w")
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write(dom_document.toString())
        file.close()

    def create(self, data):
        self.projDataDict = data

        self.start()


class Projects(QtWidgets.QWidget):

    def __init__(self, useData, busyWidget, library, settingsWidget, app,
                 projectWindowStack, projectTitleBox, parent):
        QtWidgets.QWidget.__init__(self, parent)

        self.createProjectThread = CreateProjectThread()
        self.createProjectThread.finished.connect(self.finalizeNewProject)

        self.newProjectDialog = NewProjectDialog(useData, self)
        self.newProjectDialog.projectDataReady.connect(self.createProject)

        self.busyWidget = busyWidget
        self.useData = useData
        self.app = app
        self.projectWindowStack = projectWindowStack
        self.projectTitleBox = projectTitleBox
        self.library = library
        self.settingsWidget = settingsWidget
        self.pycoder = parent

    def closeProgram(self):
        self.pycoder.close()

    def readProject(self, path):
        # validate project
        project_file = os.path.join(path, "project.xml")
        if os.path.exists(project_file) is False:
            return False
        # FIXME QtXml is no longer supported.
        dom_document = QtXml.QDomDocument()
        file = open(os.path.join(path, "project.xml"), "r")
        dom_document.setContent(file.read())
        file.close()

        data = {}

        elements = dom_document.documentElement()
        node = elements.firstChild()
        while node.isNull() is False:
            tag = node.toElement()
            name = tag.tagName()
            data["Version"] = tag.attribute("Version")
            data["Type"] = tag.attribute("Type")
            data["Name"] = tag.attribute("Name")
            data["MainScript"] = tag.attribute("MainScript")
            node = node.nextSibling()

        if name != "pycoder_project":
            return False
        else:
            return name, data

    def loadProject(self, path, show, new):
        if not self.pycoder.showProject(path):
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
            projectPathDict = {
                "notes": os.path.join(path, "Data", "wpad.txt"),
                "session": os.path.join(path, "Data", "session.xml"),
                "usedata": os.path.join(path, "Data", "usedata.xml"),
                "windata": os.path.join(path, "Data", "windata.xml"),
                "projectdata": os.path.join(path, "Data", "projectdata.xml"),
                "snippetsdir": os.path.join(path, "Data", "templates"),
                "tempdir": os.path.join(path, "temp"),
                "backupdir": os.path.join(path, "temp", "Backup", "Files"),
                "backupfile": os.path.join(path, "temp", "Backup", "bak"),
                "sourcedir": os.path.join(path, "src"),
                "ropeFolder": "../Rope",
                "buildprofile": os.path.join(path, "Build", "profile.xml"),
                "ropeprofile": os.path.join(path, "Rope", "profile.xml"),
                "projectmainfile": os.path.join(path, "project.xml"),
                "iconsdir": os.path.join(path, "Resources", "Icons"),
                "root": path
                }

            if sys.platform == 'win32':
                projectPathDict["venvdir"] = os.path.join(path,
                               "Resources", "VirtualEnv", "Windows", "Venv")
            elif sys.platform == 'darwin':
                projectPathDict["venvdir"] = os.path.join(path,
                               "Resources", "VirtualEnv", "Mac", "Venv")
            else:
                projectPathDict["venvdir"] = os.path.join(path,
                               "Resources", "VirtualEnv", "Linux", "Venv")

            try:
                project_data = self.readProject(path)
                if project_data is False:
                    QtWidgets.QApplication.restoreOverrideCursor()
                    message = QtWidgets.QMessageBox.warning(self, _("Open Project"),
                                                        _("Failed:\n\n") + path)
                    return
                projectPathDict["name"] = project_data[1]["Name"]
                projectPathDict["type"] = project_data[1]["Type"]
                projectPathDict["mainscript"] = os.path.join(path, "src",
                               project_data[1]["MainScript"])
                if sys.platform == 'win32':
                    projectPathDict["builddir"] = os.path.join(
                        path, "Build", "Windows")
                elif sys.platform == 'darwin':
                    projectPathDict["builddir"] = os.path.join(
                        path, "Build", "Mac")
                else:
                    projectPathDict["builddir"] = os.path.join(
                        path, "Build", "Linux")

                p_name = os.path.basename(path)

                projectWindow = EditorWindow(projectPathDict, self.library,
                                             self.busyWidget, self.settingsWidget.colorScheme,
                                             self.useData, self.app, self)
                if new:
                    projectWindow.editorTabWidget.loadfile(
                        projectPathDict["mainscript"])
                else:
                    projectWindow.restoreSession()
                projectWindow.editorTabWidget.updateWindowTitle.connect(
                    self.pycoder.updateWindowTitle)

                self.pycoder.addProject(projectWindow, p_name)

                if path in self.useData.OPENED_PROJECTS:
                    self.useData.OPENED_PROJECTS.remove(path)
                    self.useData.OPENED_PROJECTS.insert(0, path)
                else:
                    self.useData.OPENED_PROJECTS.insert(0, path)
                if show:
                    self.pycoder.showProject(path)
            except Exception as err:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                logging.error(
                    repr(traceback.format_exception(exc_type, exc_value,
                             exc_traceback)))
                QtWidgets.QApplication.restoreOverrideCursor()
                message = QtWidgets.QMessageBox.warning(self, _("Failed Open"),
                                                    _("Problem opening project: \n\n") + str(err))
            QtWidgets.QApplication.restoreOverrideCursor()

    def closeProject(self):
        window = self.projectWindowStack.currentWidget()
        path = window.projectPathDict["root"]
        closed = window.closeWindow()
        if closed:
            self.pycoder.removeProject(window)
            self.useData.OPENED_PROJECTS.remove(path)

    def createProject(self, data):
        self.createProjectThread.create(data)
        self.busyWidget.showBusy(True, _("Creating project... please wait!"))

    def finalizeNewProject(self):
        self.busyWidget.showBusy(False)
        if self.createProjectThread.error is not False:
            message = QtWidgets.QMessageBox.warning(self, _("New Project"),
                                                _("Failed to create project:\n\n") + self.createProjectThread.error)
        else:
            projectPath = os.path.normpath(
                self.createProjectThread.projectPath)  # otherwise an error will occur in rope
            self.loadProject(projectPath, True, True)
