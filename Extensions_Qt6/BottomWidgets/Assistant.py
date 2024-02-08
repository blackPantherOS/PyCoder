import os
import ast
from PyQt6 import QtCore, QtGui, QtWidgets
from pyflakes.checker import Checker as flakeChecker

try:
    import autopep8
except:
    from Xtra import autopep8

try:
    import pycodestyle as pep8
except:
    from Xtra import pycodestyle as pep8

try:
    from autopep8 import FixPEP8
except:
    from Xtra.autopep8 import FixPEP8

class ErrorCheckerThread(QtCore.QThread):

    newAlerts = QtCore.pyqtSignal(list, bool)

    def run(self):
        messages = []
        try:
            warnings = flakeChecker(ast.parse(self.source))
            warnings.messages.sort(key=lambda a: a.lineno)
            for warning in warnings.messages:
                fname = warning.filename
                lineno = warning.lineno
                message = warning.message
                args = warning.message_args
                messages.append((lineno, message % (args), args))
            self.newAlerts.emit(messages, False)
        except Exception as err:
            if hasattr(err, 'msg'):
                msg = err.msg.capitalize() + '.'
            else:
                msg = str(err).capitalize() + '.'
    
            # Módosítás: Az 'AttributeError' típusú kivételt külön kezeljük
            if isinstance(err, AttributeError):
                line = -1  # vagy bármilyen más jelző érték
            else:
                line = getattr(err, 'lineno', -1)

            # Módosítás: Az 'args' tuple hosszának ellenőrzése
                args_tuple = getattr(err, 'args', [None, None, None])
            offset = args_tuple[1] if len(args_tuple) > 1 and args_tuple[1] is not None else -1

            messages.append((1, line, msg, None, offset))
            self.newAlerts.emit(messages, True)


    def run_old(self):
        messages = []
        try:
            warnings = flakeChecker(ast.parse(self.source))
            warnings.messages.sort(key=lambda a: a.lineno)
            for warning in warnings.messages:
                fname = warning.filename
                lineno = warning.lineno
                message = warning.message
                args = warning.message_args
                messages.append((lineno, message % (args), args))
            self.newAlerts.emit(messages, False)
        except Exception as err:
            error_text = err.args[1][3]
            msg = err.msg.capitalize() + '.'
            line = err.lineno
            offset = err.args[1][2]

            messages.append((1, line, msg, None, offset))
            self.newAlerts.emit(messages, True)

    def runCheck(self, source):
        self.source = source

        self.start()


class Pep8CheckerThread(QtCore.QThread):

    newAlerts = QtCore.pyqtSignal(list)

    def run(self):
        checkList = []
        try:
            styleGuide = pep8.StyleGuide(reporter=Pep8Report)
            report = styleGuide.check_files([os.path.join("temp", "temp8.py")])
            for i in report.all_errors:
                fname = i[0]
                lineno = i[1]
                offset = i[2]
                code = i[3]
                error = i[4]

                if code is None:
                    # means the code has been marked to be ignored
                    continue
                checkList.append((fname, lineno, offset, code, error))
        except:
            pass
        self.newAlerts.emit(checkList)

    def runCheck(self):
        self.start()


class Pep8Report (pep8.BaseReport):

    def __init__(self, options):
        super(Pep8Report, self).__init__(options)

        self.all_errors = []

    def error(self, line_number, offset, text, check):
        code = super(Pep8Report, self).error(line_number, offset, text, check)

        err = (self.filename, line_number, offset, code, text)
        self.all_errors.append(err)

class AutoPep8FixerThread(QtCore.QThread):

    new = QtCore.pyqtSignal()

    def run(self):
        try:
            class Options(object):
                def __init__(self):
                    self.in_place = True
                    self.pep8_passes = -1
                    self.list_fixes = None
                    self.jobs = 0
                    self.ignore = []
                    self.verbose = 0
                    self.diff = None
                    self.select = []
                    self.exclude = []
                    self.aggressive = 2
                    self.line_range = []
                    self.recursive = None
                    self.max_line_length= 79
                    self.indent_size = 4
                    self.experimental = False

            options = Options()
            file = os.path.join("temp", "temp8.py")
            
            autopep8.fix_file(file, options)
            self.new.emit()
        except:
            pass

    def runFix(self):
        self.start()


class Pep8View(QtWidgets.QTreeWidget):

    def __init__(self, editorTabWidget, parent=None):
        QtWidgets.QTreeWidget.__init__(self, parent)

        self.editorTabWidget = editorTabWidget

        self.fixerThread = AutoPep8FixerThread()
        self.fixerThread.new.connect(self.autoPep8Done)

        self.setColumnCount(3)
        self.setHeaderLabels(["", "#", "Style Guide"])
        self.setAutoScroll(True)
        self.setColumnWidth(0, 50)
        self.setColumnWidth(1, 50)

        self.createActions()

    def autoPep8Done(self):
        self.editorTabWidget.busyWidget.showBusy(False)
        
        editor = self.editorTabWidget.getEditor()
        file = open(os.path.join("temp", "temp8.py"), "r")
        editor.setText(file.read())
        file.close()
        self.editorTabWidget.getEditor().removeBookmarks()
        self.editorTabWidget.enableBookmarkButtons(False)

    def contextMenuEvent(self, event):
        selectedItems = self.selectedItems()
        if len(selectedItems) > 0:
            item = selectedItems[0]
            fixable = item.data(9, 2)
            # self.fixAct.setEnabled(fixable)
            # self.fixAllAct.setEnabled(fixable)
            self.contextMenu.exec_(event.globalPos())

    def fixErrors(self):
        # just in case autopep8 check has not been done already
        saved = self.editorTabWidget.saveToTemp('pep8')
        #if saved:
            #self.pep8CheckerThread.runCheck()
        self.fixerThread.runFix()
        self.editorTabWidget.busyWidget.showBusy(True,
                                                 "Applying Style Guide... please wait!")

    def createActions(self):
        self.fixAct = QtGui.QAction(
            "Fix Selected (Not Ready)", self, statusTip="Fix Selected")
        self.fixAct.setDisabled(True)

        self.fixAllAct = \
            QtGui.QAction(
                "Fix All Occurrences (Not Ready)", self, statusTip="Fix All Occurrences")
        self.fixAllAct.setDisabled(True)

        self.fixModuleAct = \
            QtGui.QAction(
                "Fix All Issues", self, statusTip="Fix All Issues",
                triggered=self.fixErrors)

        self.contextMenu = QtWidgets.QMenu()
        self.contextMenu.addAction(self.fixAct)
        self.contextMenu.addAction(self.fixAllAct)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.fixModuleAct)


class NoAssistanceWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)

        mainLayout = QtWidgets.QHBoxLayout()
        self.setLayout(mainLayout)

        mainLayout.addStretch(1)

        label = QtWidgets.QLabel('No Assistance')
        label.setScaledContents(True)
        label.setMinimumWidth(200)
        label.setMinimumHeight(25)
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        mainLayout.addWidget(label)

        mainLayout.addStretch(1)


class Assistant(QtWidgets.QStackedWidget):

    def __init__(self, editorTabWidget, bottomStackSwitcher, parent=None):
        QtWidgets.QStackedWidget.__init__(self, parent)

        self.useData = editorTabWidget.useData
        self.refactor = editorTabWidget.refactor

        self.currentCodeIsPython = False

        supportedFixes = autopep8.supported_fixes()
        self.autopep8SupportDict = {}
        for i in supportedFixes:
            self.autopep8SupportDict[i[0]] = i[1]

        self.addWidget(NoAssistanceWidget())

        self.errorView = QtWidgets.QTreeWidget()
        self.errorView.setColumnCount(3)
        self.errorView.setHeaderLabels(["", "#", "Alerts"])
        self.errorView.setAutoScroll(True)
        self.errorView.setColumnWidth(0, 50)
        self.errorView.setColumnWidth(1, 50)
        self.errorView.itemPressed.connect(self.alertPressed)

        self.addWidget(self.errorView)

        self.pep8View = Pep8View(editorTabWidget)
        self.pep8View.itemPressed.connect(self.pep8Pressed)
        self.addWidget(self.pep8View)

        self.codeCheckerTimer = QtCore.QTimer()
        self.codeCheckerTimer.setSingleShot(True)
        self.codeCheckerTimer.timeout.connect(self.runCheck)

        self.editorTabWidget = editorTabWidget
        self.editorTabWidget.currentEditorTextChanged.connect(
            self.startCodeCheckerTimer)
        self.editorTabWidget.currentChanged.connect(self.changeWorkingMode)

        self.bottomStackSwitcher = bottomStackSwitcher

        self.codeCheckerThread = ErrorCheckerThread()
        self.codeCheckerThread.newAlerts.connect(self.updateAlertsView)

        self.pep8CheckerThread = Pep8CheckerThread()
        self.pep8CheckerThread.newAlerts.connect(self.updatePep8View)

        if self.useData.SETTINGS["EnableAssistance"] == "False":
            self.setCurrentIndex(0)
        else:
            if self.useData.SETTINGS["EnableAlerts"] == "True":
                self.setCurrentIndex(1)
            if self.useData.SETTINGS["enableStyleGuide"] == "True":
                self.setCurrentIndex(2)

        self.extendedErrorsCount = 0
        self.alertsCount = 0

    def startCodeCheckerTimer(self):
        self.codeCheckerTimer.start(500)

    def setAssistance(self, index=None):
        if index is None:
            if self.useData.SETTINGS["EnableAlerts"] == "True":
                self.setCurrentIndex(1)
            if self.useData.SETTINGS["enableStyleGuide"] == "True":
                self.setCurrentIndex(2)
        else:
            self.setCurrentIndex(index)

        self.bottomStackSwitcher.setCount(self, '')

        self.startTimer()

    def changeWorkingMode(self):
        if self.editorTabWidget.getEditorData("fileType") == "python":
            self.currentCodeIsPython = True
            self.codeCheckerTimer.start()
        else:
            self.currentCodeIsPython = False
            self.errorView.clear()
            self.pep8View.clear()
            self.bottomStackSwitcher.setCount(self, '')

    def startTimer(self):
        if self.currentCodeIsPython:
            self.codeCheckerTimer.start()

    def updateAlertsView(self, alertsList, critical):
        if self.currentCodeIsPython:
            self.errorView.clear()
            editor = self.editorTabWidget.getEditor()
            editor.clearErrorMarkerAndIndicator()
            if critical:
                item = alertsList[0]
                item = self.createItem(item[0], item[
                                       1], item[2], item[3], item[4])
                self.errorView.addTopLevelItem(item)

                lineno = int(item.text(1)) - 1
                # crashfix by vector
                offset = item.data(10, 2)[1]
                #print ("Debug ", offset)
                msg = item.text(2)

                lineText = editor.text(lineno)
                l = len(lineText)
                startPos = l - len(lineText.lstrip())

                editor.markerAdd(lineno, 9)
                self.editorTabWidget.updateEditorData("errorLine", lineno)
                editor.fillIndicatorRange(lineno, startPos, lineno,
                                          offset, editor.syntaxErrorIndicator)
                editor.annotate(lineno, msg.capitalize(),
                                editor.annotationErrorStyle)
                self.bottomStackSwitcher.setCurrentWidget(self)
            else:
                for i in alertsList:
                    item = self.createItem(0, i[0], i[1], i[2])
                    self.errorView.addTopLevelItem(item)
                self.editorTabWidget.updateEditorData("errorLine", None)
            self.bottomStackSwitcher.setCount(self, str(len(alertsList)))
            if len(alertsList) == 0:
                parentItem = QtWidgets.QTreeWidgetItem()
                item = QtWidgets.QTreeWidgetItem()
                item.setText(2, "<No Alerts>")
                item.setFlags(QtCore.Qt.ItemFlag.NoItemFlags)
                parentItem.addChild(item)
                self.errorView.addTopLevelItem(parentItem)
                parentItem.setExpanded(True)

    def createItem(self, itemType, line, message, args=None, offset=None):
        item = QtWidgets.QTreeWidgetItem(itemType)
        if itemType == 0:
            item.setIcon(0, QtGui.QIcon(
                os.path.join("Resources", "images", "alerts", "_0035_Flashlight")))
        elif itemType == 1:
            item.setIcon(0, QtGui.QIcon(
                os.path.join("Resources", "images", "alerts", "construction")))
        item.setText(1, str(line))
        item.setText(2, message)
        item.setData(10, 2, offset)
        item.setData(10, 3, args)

        return item

    def updatePep8View(self, checkList):
        if self.currentCodeIsPython:
            self.pep8View.clear()
            for i in checkList:
                item = QtWidgets.QTreeWidgetItem()
                if i[3] in self.autopep8SupportDict:
                    icon = QtGui.QIcon(
                        os.path.join("Resources", "images", "security", "allowed"))
                    item.setData(9, 2, True)
                else:
                    icon = QtGui.QIcon(
                        os.path.join("Resources", "images", "security", "requesting"))
                    item.setData(9, 2, False)
                item.setIcon(0, icon)
                item.setText(1, str(i[1]))
                item.setText(2, i[4])
                item.setData(10, 2, i[2])
                item.setData(11, 2, i[3])
                self.pep8View.addTopLevelItem(item)
            if len(checkList) == 0:
                parentItem = QtWidgets.QTreeWidgetItem()
                item = QtWidgets.QTreeWidgetItem()
                item.setText(2, "<No Issues>")
                item.setFlags(QtCore.Qt.NoItemFlags)
                parentItem.addChild(item)
                self.pep8View.addTopLevelItem(parentItem)
                parentItem.setExpanded(True)
            self.bottomStackSwitcher.setCount(self,
                                              str(len(checkList)))

    def alertPressed(self, item):
        # XXX: Fixme this only works if args is not empty
        lineno = int(item.text(1)) - 1
        word = item.data(10, 3)
        editor = self.editorTabWidget.focusedEditor()
        text = editor.text(lineno)
        if word is None:
            editor.showLine(lineno)
        else:
            word = word[0]
            start = text.find(word)
            end = start + len(word)
            editor.setSelection(lineno, start, lineno, end)
        editor.ensureLineVisible(lineno)

    def pep8Pressed(self, item):
        lineno = int(item.text(1)) - 1
        self.editorTabWidget.showLine(lineno)

    def runCheck(self):
        if self.useData.SETTINGS["EnableAssistance"] == "False":
            return
        if self.useData.SETTINGS["EnableAlerts"] == "True":
            self.codeCheckerThread.runCheck(self.editorTabWidget.getSource())
        if self.useData.SETTINGS["enableStyleGuide"] == "True":
            saved = self.editorTabWidget.saveToTemp('pep8')
            if saved:
                self.pep8CheckerThread.runCheck()
