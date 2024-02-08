import os
import sys
import traceback
import logging
import cx_Freeze
from cx_Freeze import Freezer
from PyQt6 import QtCore, QtGui, QtWidgets

sys.setrecursionlimit(5000)

class Metadata(object):
    def __init__(self):
        object.__init__(self)


class BuildThread(QtCore.QThread):
    def run(self):
        self.error = None

        metadata = Metadata()
        metadata.version = self.profile["version"]
        metadata.long_description = self.profile["comments"]
        metadata.description = self.profile["description"]
        metadata.author = self.profile["author"]
        metadata.name = self.profile["name"]

        if self.profile["base"] == "Console":
            base = "ConsoleKeepPath"
        else:
            base = "Win32GUI" if sys.platform.startswith("win") else None
        initScript = None

        if self.profile["icon"] in os.listdir(self.projectPathDict['iconsdir']):
            iconPath = os.path.join(self.projectPathDict['iconsdir'], self.profile["icon"])
        else:
            iconPath = None

        if self.profile["compress"] == 'Compress':
            compress = True
        else:
            compress = False

        if self.profile["optimize"] == "Don't Optimize":
            optimizeFlag = 0
        elif self.profile["optimize"] == 'Optimize':
            optimizeFlag = 1
        elif self.profile["optimize"] == "Optimize (Remove Doc Strings)":
            optimizeFlag = 2

        if self.profile["copydeps"] == 'Copy Dependencies':
            copyDependentFiles = True
        else:
            copyDependentFiles = False

        if self.profile["appendscripttoexe"] == 'Append Script to Exe':
            appendScriptToExe = True
        else:
            appendScriptToExe = False

        if self.profile["appendscripttolibrary"] == 'Append Script to Library':
            appendScriptToLibrary = True
        else:
            appendScriptToLibrary = False

        includes = self.profile["Includes"]
        excludes = self.profile["Excludes"]
        replacePaths = self.profile["Replace Paths"]
        binIncludes = self.profile["Bin Includes"]
        binExcludes = self.profile["Bin Excludes"]
        binPathIncludes = self.profile["Bin Path Includes"]
        binPathExcludes = self.profile["Bin Path Excludes"]
        includeFiles = self.profile["Include Files"]
        zipIncludes = self.profile["Zip Includes"]
        namespacePackages = self.profile["Namespace Packages"]
        constantsModules = self.profile["Constants Modules"]
        packages = self.profile["Packages"]
        build_dir = self.projectPathDict['builddir']

        try:
            executables = [cx_Freeze.Executable(
                           self.projectPathDict['mainscript'],
                           icon=iconPath,
                           init_script=initScript,
                           base=base,)]
            options = {
                'build_exe': {
                    'build_exe': self.projectPathDict['builddir']
                }
            }


            if self.projectSettings["UseVirtualEnv"] == "True":
                venv_path = self.projectPathDict["venvdir"]
                path = [
                    self.projectPathDict['sourcedir'],
                    os.path.join(venv_path, "Scripts"),
                ]

                if sys.platform.startswith("win"):
                    path.extend([
                        os.path.join(venv_path, "Lib"),
                        os.path.join(venv_path, "Lib", "site-packages"),
                        os.path.join(venv_path, "Include")
                    ])

                else:  # Linux
                    path.append(build_dir)

            else:
                py_path = os.path.dirname(self.projectSettings["DefaultInterpreter"])
                path = [
                    self.projectPathDict['sourcedir'],
                    #os.path.join(py_path, "includes")
                ]

                if sys.platform.startswith("win"):
                    path.extend([
                        os.path.join(py_path, "DLLs"),
                        os.path.join(py_path, "libs"),
                        os.path.join(py_path, "Lib"),
                        os.path.join(py_path, "Lib", "site-packages"),
                        os.path.join(py_path, "include"),
                    ])
                else:  # Linux
                    path.append(build_dir)

            path = list(filter(None, path))

            extraPathList = []
            for i in path:
                extraPathList.extend(self.pathListFromDir(i))
            path.extend(extraPathList)

            if sys.platform.startswith("win"):
                freezer = Cx_Freeze(executables,
                                self.projectPathDict,
                                self.useData,
                                base=base,
                                icon=iconPath,
                                metadata=metadata,
                                initScript=initScript,
                                path=path,
                                compress=compress,
                                optimizeFlag=optimizeFlag,
                                copyDependentFiles=copyDependentFiles,
                                appendScriptToExe=appendScriptToExe,
                                appendScriptToLibrary=appendScriptToLibrary,
                                includes=includes,
                                excludes=excludes,
                                replacePaths=replacePaths,
                                binIncludes=binIncludes,
                                binExcludes=binExcludes,
                                binPathIncludes=binPathIncludes,
                                binPathExcludes=binPathExcludes,
                                includeFiles=includeFiles,
                                zipIncludes=zipIncludes,
                                namespacePackages=namespacePackages,
                                constantsModules=constantsModules,
                                packages=packages)


                freezer.Freeze()

                try:
                    badModules = freezer.finder._badModules
                    names = list(badModules.keys())
                    names.sort()
                    self.missing = []
                    for name in names:
                        callers = list(badModules[name].keys())
                        callers.sort()
                        self.missing.append("? {0} imported from {1}".format
                                            (name, ", ".join(callers)))
                except AttributeError:
                    print("The finder in cx_Freeze curren not available.")
            else:

                self.missing = []
                freezer = cx_Freeze.Freezer(executables,
                                target_dir=build_dir)
                freezer.freeze()

        except Exception as err:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.error(repr(traceback.format_exception(exc_type, exc_value,
                                      exc_traceback)))
            self.error = str(err)

    def pathListFromDir(self, dirPath):
        """
        This is to get the list of module search paths from .pth files
        """
        pathList = []
        for i in  os.listdir(dirPath):
            path = os.path.join(dirPath, i)
            if os.path.isfile(path):
                if i.endswith('.pth'):
                    file = open(path, 'r')
                    lines = file.readlines()
                    file.close()
                    for line in lines:
                        lineText = line.rstrip()
                        if os.path.exists(lineText):
                            pathList.append(lineText)
                        else:
                            fullPath = os.path.join(dirPath, lineText)
                            if os.path.exists(fullPath):
                                pathList.append(fullPath)

        return pathList

    def build(self, profile, projectPathDict, projectSettings, useData):
        self.profile = profile
        self.projectPathDict = projectPathDict
        self.useData = useData
        self.projectSettings = projectSettings

        targetDir=self.projectPathDict['builddir']
        if not os.path.exists(targetDir):
            os.makedirs(targetDir, exist_ok=True)

        print("Start build to target dir:", targetDir)
        self.start()

class Cx_Freeze(Freezer):
    def __init__(self, executables,
                 projectPathDict,
                 useData,
                 base,
                 icon,
                 metadata,
                 initScript,
                 path,
                 compress,
                 optimizeFlag,
                 copyDependentFiles,
                 appendScriptToExe,
                 appendScriptToLibrary,
                 includes,
                 excludes,
                 replacePaths,
                 binIncludes,
                 binExcludes,
                 binPathIncludes,
                 binPathExcludes,
                 includeFiles,
                 zipIncludes,
                 namespacePackages,
                 constantsModules,
                 packages):
        Freezer.__init__(self, executables,
                         silent=True,
                         icon=icon,
                         metadata=metadata,
                         includeMSVCR=True,
                         target_dir=projectPathDict['builddir'],
                         initScript=initScript,
                         path=path,
                         base=base,
                         compress=compress,
                         optimizeFlag=optimizeFlag,
                         copyDependentFiles=copyDependentFiles,
                         appendScriptToExe=appendScriptToExe,
                         appendScriptToLibrary=appendScriptToLibrary,
                         includes=includes,
                         excludes=excludes,
                         replacePaths=replacePaths,
                         binIncludes=binIncludes,
                         binExcludes=binExcludes,
                         binPathIncludes=binPathIncludes,
                         binPathExcludes=binPathExcludes,
                         includeFiles=includeFiles,
                         zipIncludes=zipIncludes,
                         namespacePackages=namespacePackages,
                         constantsModules=constantsModules,
                         packages=packages
                         )


class Build(QtWidgets.QWidget):
    def __init__(self, busyWidget, messagesWidget, projectPathDict, projectSettings, useData,
                 buildConfig, editorTabWidget, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        self.useData = useData
        self.projectPathDict = projectPathDict
        self.buildConfig = buildConfig
        self.projectSettings = projectSettings

        self.messagesWidget = messagesWidget
        self.busyWidget = busyWidget
        self.editorTabWidget = editorTabWidget
        self.busyWidget.cancel.connect(self.cancelBuild)

        self.buildThread = BuildThread()
        self.buildThread.finished.connect(self.buildFinished)

        self.durationTime = QtCore.QTime()

    def openDir(self):
        if os.path.exists(self.projectPathDict["builddir"]):
            if sys.platform.startswith('win'):
                os.system('start explorer "{}"'.format(self.projectPathDict["builddir"]))
            else:
                opener = "xdg-open" if sys.platform == "linux" else "open"
                os.system('{} "{}"'.format(opener, self.projectPathDict["builddir"]))
        else:
            message = QtWidgets.QMessageBox.critical(self, "Open",
                                                 "Build folder is missing!")

    def cancelBuild(self):
        self.buildThread.exit()

    def build(self):
        saved = self.editorTabWidget.saveProject()
        if saved:
            profile = self.buildConfig.load()
            self.durationTime.start()
            self.buildThread.build(profile, self.projectPathDict, self.projectSettings, self.useData)
            self.busyWidget.showBusy(True)

    def buildFinished(self):
        elapsed = self.durationTime.elapsed()
        if elapsed >= 60000:
            min = int(elapsed / 60000)
            sec = int((elapsed - (60000 * min)) / 1000)
            elapsed = "{0}m{1}s".format(str(min), str(sec))
        else:
            elapsed = str(round(elapsed / 1000, 1)) + 's'
        self.busyWidget.showBusy(False)
        if self.buildThread.error:
            self.messagesWidget.addMessage(
                1, "Build Completed in {0} [Errors]".format(str(elapsed)), 
                    [self.buildThread.error])
        else:
            if len(self.buildThread.missing) > 0:
                self.messagesWidget.addMessage(
                    1, "Build Completed in {0} [missing modules]".format(elapsed), 
                        self.buildThread.missing)
            else:
                self.messagesWidget.addMessage(
                    0, "Build Completed in {0} ".format(elapsed), 
                        ["Build Completed Successfully!"])
