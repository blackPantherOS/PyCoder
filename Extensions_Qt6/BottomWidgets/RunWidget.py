import os
import re
import sys
import locale
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.Qsci import QsciScintilla, QsciScintillaBase, QsciLexerCustom


from Extensions_Qt6.BaseScintilla import BaseScintilla
from Extensions_Qt6.PathLineEdit import PathLineEdit
from Extensions_Qt6 import Global
from Extensions_Qt6 import StyleSheet

default_encoding = locale.getpreferredencoding()


class SetRunParameters(QtWidgets.QLabel):

    def __init__(self, projectSettings, projectPathDict, useData, parent=None):
        QtWidgets.QLabel.__init__(self, parent)

        self.setMinimumSize(400, 220)

        self.setBackgroundRole(QtGui.QPalette.ColorRole.Window)
        self.setAutoFillBackground(True)
        self.setObjectName("containerLabel")
        self.setStyleSheet(StyleSheet.toolWidgetStyle)

        self.projectSettings = projectSettings
        self.useData = useData
        self.projectPathDict = projectPathDict

        mainLayout = QtWidgets.QVBoxLayout()

        hbox = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(hbox)

        label = QtWidgets.QLabel(_("Run Parameters"))
        label.setObjectName("toolWidgetNameLabel")
        hbox.addWidget(label)

        hbox.addStretch(1)

        self.hideButton = QtWidgets.QToolButton()
        self.hideButton.setAutoRaise(True)
        self.hideButton.setIcon(
            QtGui.QIcon(os.path.join("Resources", "images", "cross_")))
        self.hideButton.clicked.connect(self.hide)
        hbox.addWidget(self.hideButton)

        hbox = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(hbox)

        self.runTypeBox = QtWidgets.QComboBox()
        self.runTypeBox.addItem(_("Run"))
        self.runTypeBox.addItem(_("Profiler"))
        self.runTypeBox.addItem(_("Trace"))
        if self.projectSettings["RunType"] == 'Profiler':
            self.runTypeBox.setCurrentIndex(1)
        elif self.projectSettings["RunType"] == 'Trace':
            self.runTypeBox.setCurrentIndex(2)
        self.runTypeBox.currentIndexChanged.connect(self.saveArguments)
        self.runTypeBox.currentIndexChanged.connect(self.runTypeChanged)
        hbox.addWidget(self.runTypeBox)

        self.traceTypeBox = QtWidgets.QComboBox()
        self.traceTypeBox.addItem(_("Calling relationships"))
        self.traceTypeBox.addItem(_("Functions called"))
        self.traceTypeBox.addItem(_("Times lines are called"))
        self.traceTypeBox.addItem(_("View currently running line of code"))
        self.traceTypeBox.setCurrentIndex(int(
            self.projectSettings["TraceType"]))
        self.traceTypeBox.currentIndexChanged.connect(self.saveArguments)
        hbox.addWidget(self.traceTypeBox)

        if self.runTypeBox.currentIndex() != 2:
            self.traceTypeBox.hide()

        self.runWithArgsBox = QtWidgets.QCheckBox(_("Arguments:"))
        if self.projectSettings["RunWithArguments"] == 'True':
            self.runWithArgsBox.setChecked(True)
        self.runWithArgsBox.toggled.connect(self.saveArguments)
        mainLayout.addWidget(self.runWithArgsBox)

        self.argumentsLine = PathLineEdit()
        self.argumentsLine.setText(self.projectSettings["RunArguments"])
        self.argumentsLine.textChanged.connect(self.saveArguments)
        mainLayout.addWidget(self.argumentsLine)

        hbox = QtWidgets.QHBoxLayout()

        self.clearOutputBox = QtWidgets.QCheckBox(_("Clear output window"))
        if self.projectSettings["ClearOutputWindowOnRun"] == 'True':
            self.clearOutputBox.setChecked(True)
        self.clearOutputBox.toggled.connect(self.saveArguments)
        hbox.addWidget(self.clearOutputBox)

        hbox.addStretch(1)

        hbox.addWidget(QtWidgets.QLabel(_("Max Output Size <lines>")))

        self.bufferSizeBox = QtWidgets.QSpinBox()
        self.bufferSizeBox.setMaximum(999)
        self.bufferSizeBox.setMinimumWidth(100)
        self.bufferSizeBox.setValue(int(self.projectSettings['BufferSize']))
        self.bufferSizeBox.valueChanged.connect(self.saveArguments)
        hbox.addWidget(self.bufferSizeBox)

        mainLayout.addLayout(hbox)

        self.runPointBox = QtWidgets.QComboBox()
        self.runPointBox.addItem(_("Internal Console"))
        self.runPointBox.addItem(_("External Console"))
        if self.projectSettings["RunInternal"] == 'False':
            self.runPointBox.setCurrentIndex(1)
        self.runPointBox.currentIndexChanged.connect(self.saveArguments)
        mainLayout.addWidget(self.runPointBox)

        self.useVirtualEnvBox = QtWidgets.QCheckBox(_("Use Virtual Environment"))
        if self.projectSettings["UseVirtualEnv"] == 'True':
            self.useVirtualEnvBox.setChecked(True)
        self.useVirtualEnvBox.toggled.connect(self.setDefaultInterpreter)
        mainLayout.addWidget(self.useVirtualEnvBox)

        hbox = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(hbox)

        self.installedPythonVersionBox = QtWidgets.QComboBox()
        self.installedPythonVersionBox.setMinimumWidth(200)
        self.updateInstalledInterpreters()
        self.installedPythonVersionBox.currentIndexChanged.connect(
            self.setDefaultInterpreter)
        hbox.addWidget(self.installedPythonVersionBox)

        hbox.addStretch(1)

        label = QtWidgets.QLabel("Installed Python")
        hbox.addWidget(label)

        self.setLayout(mainLayout)

        self.setDefaultInterpreter()

    def updateInstalledInterpreters(self):
        self.installedPythonVersionBox.clear()
        if len(self.useData.SETTINGS["InstalledInterpreters"]) > 0:
            for i in self.useData.SETTINGS["InstalledInterpreters"]:
                self.installedPythonVersionBox.addItem(i)
                if self.projectSettings["UseVirtualEnv"] == 'False':
                    index = self.installedPythonVersionBox.findText(
                        self.projectSettings["DefaultInterpreter"])
                    if index != -1:
                        self.installedPythonVersionBox.setCurrentIndex(index)
        else:
            self.installedPythonVersionBox.addItem(_("<No Python installed>"))

    def runTypeChanged(self, index):
        if index == 2:
            self.traceTypeBox.show()
        else:
            self.traceTypeBox.hide()

    def saveArguments(self):
        self.projectSettings["RunWithArguments"] = str(
            self.runWithArgsBox.isChecked())
        self.projectSettings[
            "RunArguments"] = self.argumentsLine.text().strip()
        self.projectSettings["ClearOutputWindowOnRun"] = str(
            self.clearOutputBox.isChecked())
        self.projectSettings["BufferSize"] = str(self.bufferSizeBox.value())
        self.projectSettings["RunType"] = self.runTypeBox.currentText()
        self.projectSettings["RunInternal"] = str(
            self.runPointBox.currentIndex() == 0)
        self.projectSettings["TraceType"] = str(
            self.traceTypeBox.currentIndex())

    def setDefaultInterpreter(self):
        if self.useVirtualEnvBox.isChecked():
            # FIXME: Needs to be corrected for each platform
            if sys.platform == 'win32':
                self.projectSettings["DefaultInterpreter"] = \
                    os.path.join(self.projectPathDict["venvdir"],
                                     "Scripts", "python.exe")
            elif sys.platform == 'darwin':
                self.projectSettings["DefaultInterpreter"] = \
                    os.path.join(self.projectPathDict["venvdir"],
                                     "Scripts", "python")
            else:
                self.projectSettings["DefaultInterpreter"] = \
                    os.path.join(self.projectPathDict["venvdir"],
                                     "Scripts", "python3")
        else:
            if len(self.useData.SETTINGS["InstalledInterpreters"]) > 0:
                self.projectSettings["DefaultInterpreter"] = \
                    self.installedPythonVersionBox.currentText()
            else:
                self.projectSettings["DefaultInterpreter"] = '/usr/bin/python3'
        self.projectSettings["UseVirtualEnv"] = str(
            self.useVirtualEnvBox.isChecked())


class OutputLexer(QsciLexerCustom):

    def __init__(self, parent=None):
        QsciLexerCustom.__init__(self, parent)

        self._styles = {
            0: 'Default',
            1: 'ErrorInfo',
            2: 'OutputInfo',
            3: 'ExitInfo',
            4: 'Start'
            }
        for key in self._styles:
            setattr(self, self._styles[key], key)

    def description(self, style):
        return self._styles.get(style, '')

    def defaultColor(self, style):
        if style == self.Default:
            return QtGui.QColor('#ffffff')
        elif style == self.ErrorInfo:
            return QtGui.QColor('#E6DB74')
        elif style == self.OutputInfo:
            return QtGui.QColor('#FFFFFF')
        elif style == self.ExitInfo:
            return QtGui.QColor('#3DA3EF')
        elif style == self.Start:
            return QtGui.QColor('#7FE22A')
        return QsciLexerCustom.defaultColor(self, style)

    def defaultFont(self, style):
        if style == self.Default:
            return Global.getDefaultFont()
        elif style == self.ErrorInfo:
            return Global.getDefaultFont()
        elif style == self.OutputInfo:
            return Global.getDefaultFont()
        elif style == self.ExitInfo:
            return Global.getDefaultFont()
        elif style == self.Start:
            return Global.getDefaultFont()
        return QsciLexerCustom.defaultFont(self, style)

    def defaultPaper(self, style):
        return QtGui.QColor('#000000')

    def defaultEolFill(self, style):
        return True

    def styleText(self, start, end):
        editor = self.editor()
        if editor is None:
            return

        # scintilla works with encoded bytes, not decoded characters.
        # this matters if the source contains non-ascii characters and
        # a multi-byte encoding is used (e.g. utf-8)
        source = ''
        if end > editor.length():
            end = editor.length()
        if end > start:
            if sys.hexversion >= 0x02060000:
                # faster when styling big files, but needs python 2.6
                source = bytearray(end - start)
                editor.SendScintilla(
                    editor.SCI_GETTEXTRANGE, start, end, source)
            else:
                source = editor.text().encode('utf-8')
        if not source:
            return

        set_style = self.setStyling
        self.startStyling(start, 0x1f)


class RunWidget(BaseScintilla):

    loadProfile = QtCore.pyqtSignal()

    def __init__(
        self, bottomStackSwitcher, projectData, useData, editorTabWidget, vSplitter, runProjectAct, stopRunAct,
            runFileAct, parent=None):
        BaseScintilla.__init__(self, parent)

        self.projectData = projectData
        self.runProjectAct = runProjectAct
        self.stopRunAct = stopRunAct
        self.runFileAct = runFileAct
        self.editorTabWidget = editorTabWidget
        self.parent = parent
        self.vSplitter = vSplitter
        self.bottomStackSwitcher = bottomStackSwitcher
        self.useData = useData

        self.profileMode = False
        self.tracebackRe = re.compile(r'(\s)*File "(.*?)", line \d.+')

        self.setMarginWidth(1, 0)
        self.toggleInsertOrOvertype()

        self.linkIndicator = self.indicatorDefine(
            QsciScintilla.IndicatorStyle.PlainIndicator, 8)
        self.setIndicatorForegroundColor(QtGui.QColor(
            "#474747"), self.linkIndicator)
        self.setIndicatorDrawUnder(True, self.linkIndicator)

        self.lexer = OutputLexer(self)
        self.setLexer(self.lexer)
        self.setFont(Global.getDefaultFont())
        self.openMode = QtCore.QIODeviceBase.OpenModeFlag.ReadWrite
        self.currentProcess = None

        self.setCaretForegroundColor(QtGui.QColor("#ffffff"))
        self.setWrapMode(QsciScintilla.WrapMode.WrapWord)

        self.setSelectionBackgroundColor(QtGui.QColor("#391EE8"))
        self.setSelectionForegroundColor(QtGui.QColor("#FFFFFF"))

        self.runProcess = QtCore.QProcess(self)
        #self.runProcess.error.connect(self.writeProcessError)
        self.runProcess.stateChanged.connect(self.stateChanged)
        self.runProcess.readyReadStandardOutput.connect(self.writeOutput)
        self.runProcess.readyReadStandardError.connect(self.writeError)
        self.runProcess.started.connect(self.processStarted)
        self.runProcess.finished.connect(self.writeExitStatus)
        self.runProcess.finished.connect(self.processEnded)

        self.copyAct = QtGui.QAction(_("Copy"), self,
                                     statusTip=_("Copy"), triggered=self.copyText)
        self.contextMenu = QtWidgets.QMenu()
        self.contextMenu.addAction(self.copyAct)

        self.setReadOnly(True)
        self.blocking_cursor_pos = (0, 0)

        self.setStyleSheet("QsciScintilla {border: none;}")

    def leaveEvent(self, event):
        self.clearAllIndicators(self.linkIndicator)

        super(RunWidget, self).leaveEvent(event)

    def mouseMoveEvent(self, event):
        position = event.pos()
        x = position.x()
        y = position.y()
    
        line = self.getHoveredLine(x, y)
        lineText = self.text(line)
    
        l = len(lineText)
        offset = l - len(lineText.lstrip())
    
        self.clearAllIndicators(self.linkIndicator)
    
        if self.tracebackRe.match(lineText):
            self.fillIndicatorRange(
                line, offset, line, (l - 1), self.linkIndicator)
    
        super(RunWidget, self).mouseMoveEvent(event)
    
    def mouseMoveEvent_old(self, event):
        x = event.x()
        y = event.y()

        line = self.getHoveredLine(x, y)
        lineText = self.text(line)

        l = len(lineText)
        offset = l - len(lineText.lstrip())

        self.clearAllIndicators(self.linkIndicator)

        if self.tracebackRe.match(lineText):
            self.fillIndicatorRange(
                line, offset, line, (l - 1), self.linkIndicator)

        super(RunWidget, self).mouseMoveEvent(event)

    def copyText(self):
        cb = self.editorTabWidget.app.clipboard()
        if self.hasSelectedText():
            cb.setText(self.selectedText())
        else:
            cb.setText(self.text())

    def stateChanged(self, newState):
        if newState == 2:
            self.vSplitter.showRunning()
            self.setReadOnly(False)
        else:
            self.setReadOnly(True)

    def insertInput(self, text):
        self.append('\n')
        data = QtCore.QByteArray()
        data.append(bytes(text + '\n', encoding="utf-8"))
        self.runProcess.write(data)

    def writeProcessError(self, processError):
        self.writeOutput()
        self.writeError()
        if processError == 0:
            self.printout(">>> FailedToStart!\n", 3)
        elif processError == 1:
            self.printout(">>> Crashed!\n", 3)
        elif processError == 2:
            self.printout(">>> Timedout!\n", 3)
        elif processError == 3:
            self.printout(">>> WriteError!\n", 3)
        elif processError == 4:
            self.printout(">>> ReadError!\n", 3)
        elif processError == 5:
            self.printout(">>> UnknownError!\n", 3)
        self.bottomStackSwitcher.setCurrentWidget(self)

    def writeOutput(self):
        while self.runProcess.canReadLine():
            if self.currentProcess is None:
                break
            text = self.runProcess.readLine().data().decode(
                default_encoding)
            self.printout(text, 2)

    def writeError(self):
        text = \
            self.runProcess.readAllStandardError().data().decode(
                default_encoding)
        self.printout(text, 1)
        self.bottomStackSwitcher.setCurrentWidget(self)

    def writeExitStatus(self, exitCode, exitStatus):
        self.writeOutput()
        self.writeError()
        if exitStatus == QtCore.QProcess.ExitStatus.NormalExit:
            self.printout(">>> Exit: {0}\n".format(str(exitCode)), 3)
        else:
            # error will be displayed instead by writeProcessError
            pass
        self.currentProcess = None
        if exitCode == 1:
            self.vSplitter.showError()
        else:
            self.vSplitter.showNormal()

    def processStarted(self):
        self.runProjectAct.setVisible(False)
        self.stopRunAct.setVisible(True)
        self.runFileAct.setEnabled(False)

    def processEnded(self):
        self.runProjectAct.setVisible(True)
        self.stopRunAct.setVisible(False)
        self.runFileAct.setEnabled(True)

        self.currentProcess = None
        if self.profileMode:
            self.loadProfile.emit()
            self.profileMode = False

    def printout(self, text, styleNum):
        start = self.length()
        self.SendScintilla(QsciScintillaBase.SCI_STARTSTYLING, start)
        self.append(text)
        self.recolor(start, -1)
        self.SendScintilla(QsciScintillaBase.SCI_SETSTYLING, len(text),
                           styleNum)
        QtCore.QCoreApplication.processEvents()
        self.setFirstVisibleLine(self.lines())
        self.blocking_cursor_pos = self.position('eof')
        self.setCursorPosition(self.blocking_cursor_pos[
                               0], self.blocking_cursor_pos[1])

    def pythonPath(self):
        if self.projectData["DefaultInterpreter"] == "None":
            message = QtWidgets.QMessageBox.critical(
                self, _("Run"), _("No Python interpreter to run your code. Please install Python."))
            return None
        else:
            if os.path.exists(self.projectData["DefaultInterpreter"]):
                if len(self.useData.SETTINGS["InstalledInterpreters"]) == 0:
                    message = QtWidgets.QMessageBox.critical(
                        self, _("Run"), _("Python must be installed for virtual environment to work."))
                    return None
                else:
                    return self.projectData["DefaultInterpreter"]
            else:
                message = QtWidgets.QMessageBox.critical(
                    self, _("Run"), _("The current Python interpreter is not available."))
                return None

    def runModule(self, runScript, fileName, run_internal, run_with_args, args):
        pythonPath = self.pythonPath()
        if pythonPath is None:
            return
        env = QtCore.QProcessEnvironment().systemEnvironment()
        self.runProcess.setProcessEnvironment(env)

        if run_internal:
            self.currentProcess = fileName
            if run_with_args:
                self.printout(">>> Running: {0} <arguments={1}>\n".format(
                    self.currentProcess, args), 4)
                self.runProcess.start(pythonPath, [
                                      runScript, args], self.openMode)
            else:
                self.printout(">>> Running: {0} <arguments=None>\n".format(
                    self.currentProcess), 4)
                self.runProcess.start(pythonPath, [runScript], self.openMode)
            self.runProcess.waitForStarted()
        else:
            if run_with_args:
                self.runProcess.startDetached(
                    pythonPath, ["-i", runScript, args])
            else:
                self.runProcess.startDetached(pythonPath, ["-i", runScript])
            # -i ensures that the shell program remains even after the source program
            # has finished or has been terminated in order for debugging to be
            # done

    def runTrace(self, runScript, fileName, run_internal, run_with_args, args, option):
        pythonPath = self.pythonPath()
        if pythonPath is None:
            return

        env = QtCore.QProcessEnvironment().systemEnvironment()
        self.runProcess.setProcessEnvironment(env)

        if run_internal:
            self.currentProcess = fileName
            if run_with_args:
                self.printout(">>> Trace Execution: {0} <arguments={1}>\n".format(
                    self.currentProcess, args), 4)
            else:
                self.printout(">>> Trace Execution: {0} <arguments=None>\n".format(
                    self.currentProcess), 4)
            if option == 0:
                # calling relationships
                if run_with_args:
                    self.runProcess.start(pythonPath, ['-m', "trace",
                                                       '--trackcalls', runScript, args], self.openMode)
                else:
                    self.runProcess.start(pythonPath, ['-m', "trace",
                                                       '--trackcalls', runScript], self.openMode)
            elif option == 1:
                # functions called
                if run_with_args:
                    self.runProcess.start(pythonPath, ['-m', "trace",
                                                       '--listfuncs', runScript, args], self.openMode)
                else:
                    self.runProcess.start(pythonPath, ['-m', "trace",
                                                       '--listfuncs', runScript], self.openMode)
            elif option == 2:
                # creates a file with same code but showing how many times
                # each line of code args
                countfile = os.path.abspath(os.path.join("temp", "count.txt"))
                file = open(countfile, 'w')
                file.close()
                if run_with_args:
                    self.runProcess.start(pythonPath, ['-m', "trace",
                                                       '--count', '--file={0}'.format(countfile), runScript, args], self.openMode)
                else:
                    self.runProcess.start(pythonPath, ['-m', "trace",
                                                       '--count', '--file={0}'.format(countfile), runScript], self.openMode)
            elif option == 3:
                # show in real time what lines of code are currently being
                # executed
                if run_with_args:
                    self.runProcess.start(
                        pythonPath, ['-m', "trace", '--timing',
                                     '--trace', runScript, args], self.openMode)
                else:
                    self.runProcess.start(
                        pythonPath, ['-m', "trace", '--timing',
                                     '--trace', runScript], self.openMode)
        else:
            if option == 0:
                # calling relationships
                if run_with_args:
                    self.runProcess.startDetached(
                        pythonPath, ['-i', '-m', "trace",
                                                 '--trackcalls', runScript, args], self.openMode)
                else:
                    self.runProcess.startDetached(
                        pythonPath, ['-i', '-m', "trace",
                                                 '--trackcalls', runScript])
            elif option == 1:
                # functions called
                if run_with_args:
                    self.runProcess.startDetached(
                        pythonPath, ['-i', '-m', "trace",
                                                 '--listfuncs', runScript, args])
                else:
                    self.runProcess.startDetached(
                        pythonPath, ['-i', '-m', "trace",
                                                 '--listfuncs', runScript])
            elif option == 2:
                # creates a file with same code but showing how many times each
                # line of code runs
                if run_with_args:
                    self.runProcess.startDetached(
                        pythonPath, ['-i', '-m', "trace",
                                                 '--count', runScript, args])
                else:
                    self.runProcess.startDetached(
                        pythonPath, ['-i', '-m', "trace",
                                                 '--count', runScript])
            elif option == 3:
                # show in real time what lines of code are currently being
                # executed
                if run_with_args:
                    self.runProcess.startDetached(
                        pythonPath, ['-i', '-m', "trace",
                                                 '--timing', '--trace', runScript, args])
                else:
                    self.runProcess.startDetached(
                        pythonPath, ['-i', '-m', "trace",
                                                 '--timing', '--trace', runScript])

    def runProfiler(self, runScript, fileName, run_internal, run_with_args, args):
        pythonPath = self.pythonPath()
        if pythonPath is None:
            return
        env = QtCore.QProcessEnvironment().systemEnvironment()
        self.runProcess.setProcessEnvironment(env)

        p_args = ['-m', 'cProfile', '-o',
                  os.path.abspath(os.path.join("temp", "profile"))]
        if os.name == 'nt':
            # On Windows, one has to replace backslashes by slashes to avoid
            # confusion with escape characters (otherwise, for example, '\t'
            # will be interpreted as a tabulation):
            p_args.append(os.path.normpath(runScript).replace(os.sep, '/'))
        else:
            p_args.append(runScript)

        self.profileMode = True
        if run_internal:
            self.currentProcess = fileName
            if run_with_args:
                self.printout(">>> Profiling: {0} <arguments={1}>\n".format(
                    self.currentProcess, args), 4)
            else:
                self.printout(">>> Profiling: {0} <arguments=None>\n".format(
                    self.currentProcess), 4)
            self.runProcess.start(pythonPath, p_args)
            self.runProcess.waitForStarted()
        else:
            p_args.insert(0, "-i")
            self.runProcess.startDetached(pythonPath, p_args)
            # -i ensures that the shell program remains even after the source program
            # has finished or has been terminated in order for debugging to be
            # done

    def reRunFile(self):
        self.run(False, True)

    def runFile(self):
        saved = self.editorTabWidget.save()
        if saved:
            self.run(False)

    def runProject(self):
        if self.editorTabWidget.errorsInProject():
            reply = QtWidgets.QMessageBox.warning(self, _("Run Project"),
                                              _("There are errors in your project. Run anyway?"),
                                              QtWidgets.QMessageBox.StandardButton.Yes | 
                                              QtWidgets.QMessageBox.StandardButton.No)
            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                pass
            else:
                return
        saved = self.editorTabWidget.saveProject()
        if saved:
            pass
        else:
            return
        self.run(True)

    def run(self, project, rerun=False):
        if project:
            filePath = self.editorTabWidget.projectPathDict["mainscript"]
            fileName = self.editorTabWidget.projectPathDict["name"]
            if os.path.exists(filePath) is not True:
                message = QtWidgets.QMessageBox.warning(self, _("Run Project"),
                                                    _("Main script is missing: ") + fileName)
                return
        else:
            if self.editorTabWidget.getSource().strip() == '':
                message = QtWidgets.QMessageBox.warning(self, _("Run"),
                                                    _("Source code must be present!"))
                return
            if rerun is False:
                self.filePath = self.editorTabWidget.getEditorData("filePath")
                filePath = self.filePath
                self.fileName = self.editorTabWidget.getTabName()
                fileName = self.fileName
                self.runFileAct.setEnabled(True)
            else:
                filePath = self.filePath
                fileName = self.fileName
        cwd = os.path.dirname(filePath)
        self.runProcess.setWorkingDirectory(cwd)

        if self.projectData["RunInternal"] == "True":
            run_internal = True
        else:
            run_internal = False
        run_with_args = self.projectData["RunWithArguments"]
        if run_with_args == "True":
            run_with_args = True
        else:
            run_with_args = False
        args = self.projectData["RunArguments"]
        bufferSize = int(self.projectData["BufferSize"])

        clearOutput = self.projectData["ClearOutputWindowOnRun"]

        if clearOutput == "True":
            self.clear()
        elif self.lines() >= bufferSize:
            self.clear()
        runType = self.projectData["RunType"]
        if runType == "Run":
            self.runModule(filePath, fileName, run_internal, run_with_args,
                           args)
        if runType == "Profiler":
            self.runProfiler(filePath, fileName, run_internal, run_with_args,
                             args)
        elif runType == "Trace":
            option = int(self.projectData["TraceType"])
            self.runTrace(filePath, fileName, run_internal, run_with_args,
                          args, option)

    def stopProcess(self):
        self.runProcess.kill()
        self.currentProcess = None

    def contextMenuEvent(self, event):
        if self.isReadOnly():
            self.contextMenu.exec(event.globalPos())
        else:
            event.ignore()

    def getHoveredLine(self, x, y):
        position = self.SendScintilla(
            QsciScintilla.SCI_POSITIONFROMPOINT, x, y)
        line = self.SendScintilla(QsciScintilla.SCI_LINEFROMPOSITION, position)

        return line

    def mouseDoubleClickEvent(self, event):
        pos = event.pos()
        x = pos.x()
        y = pos.y()

        line = self.getHoveredLine(x, y)
        lineText = self.text(line)

        if self.tracebackRe.match(lineText):
            file_word_index = lineText.find('File')
            min_index = lineText.find('"') + 1
            max_index = lineText.find('"', min_index)
            path = lineText[min_index:max_index]

            max_index += 7
            line_end_index = lineText.find(',', max_index)
            lineno = int(lineText[max_index:line_end_index]) - 1

            self.editorTabWidget.loadfile(path)
            self.editorTabWidget.showLine(lineno)

        event.ignore()

    def mousePressEvent(self, event):
        if self.isReadOnly():
            super(RunWidget, self).mousePressEvent(event)
        else:
            event.ignore()

    def keyPressEvent(self, event):
        """
        Reimplemented to create a console-like interface.
        """
        line, index = self.getCursorPosition()
        key = event.key()
        ctrl = event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier
        alt = event.modifiers() & QtCore.Qt.KeyboardModifier.AltModifier
        shift_down = event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier
        if ctrl:
            pass
        elif alt:
            pass
        elif key == QtCore.Qt.Key.Key_Backspace:
            if self.getCursorPosition() == self.blocking_cursor_pos:
                pass
            else:
                QsciScintilla.keyPressEvent(self, event)
        elif key == QtCore.Qt.Key.Key_Left:
            if self.getCursorPosition() == self.blocking_cursor_pos:
                pass
            else:
                QsciScintilla.keyPressEvent(self, event)
        elif key == QtCore.Qt.Key.Key_Up:
            self.scrollVertical(-1)
        elif key == QtCore.Qt.Key.Key_Down:
            self.scrollVertical(1)
        elif key == QtCore.Qt.Key.Key_Return:
            # get input text
            text = self.getText(
                self.blocking_cursor_pos, self.position("eof"))
            self.insertInput(text)
        else:
            QsciScintilla.keyPressEvent(self, event)
