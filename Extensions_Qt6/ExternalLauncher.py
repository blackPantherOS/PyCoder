import os
from PyQt6 import QtCore, QtGui, QtWidgets

from Extensions_Qt6 import Global
from Extensions_Qt6.PathLineEdit import PathLineEdit
from Extensions_Qt6 import StyleSheet


class ExternalLauncher(QtWidgets.QLabel):

    showMe = QtCore.pyqtSignal()

    def __init__(self, externalLaunchList, parent=None):
        super(ExternalLauncher, self).__init__(parent)

        self.externalLaunchList = externalLaunchList

        self.setMinimumSize(600, 230)
        self.setObjectName("containerLabel")
        self.setStyleSheet(StyleSheet.toolWidgetStyle)

        #vector self.setBackgroundRole(QtGui.QPalette.Background)
        #palette = self.palette()
        #palette.setColor(QtGui.QPalette.Window, QtGui.QColor(255, 255, 255))  # Háttérszín beállítása
        #palette.setColor(QtGui.QPalette.ColorGroup.Normal, QtGui.QPalette.ColorRole.Window, QtGui.QColor("#FFFF00")) 
        #self.setPalette(palette)

        self.setAutoFillBackground(True)
        self.setObjectName("containerLabel")

        mainLayout = QtWidgets.QVBoxLayout()

        hbox = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(hbox)

        label = QtWidgets.QLabel("Manage Launchers")
        label.setObjectName("toolWidgetNameLabel")
        hbox.addWidget(label)

        hbox.addStretch(1)

        self.hideButton = QtWidgets.QToolButton()
        self.hideButton.setAutoRaise(True)
        self.hideButton.setIcon(
            QtGui.QIcon(os.path.join("Resources", "images", "cross_")))
        self.hideButton.clicked.connect(self.hide)
        hbox.addWidget(self.hideButton)

        self.listWidget = QtWidgets.QListWidget()
        mainLayout.addWidget(self.listWidget)

        formLayout = QtWidgets.QFormLayout()
        mainLayout.addLayout(formLayout)

        self.pathLine = PathLineEdit()
        formLayout.addRow("Path:", self.pathLine)

        self.parametersLine = QtWidgets.QLineEdit()
        formLayout.addRow("Parameters:", self.parametersLine)

        hbox = QtWidgets.QHBoxLayout()
        formLayout.addRow('', hbox)

        self.removeButton = QtWidgets.QPushButton("Remove")
        self.removeButton.clicked.connect(self.removeLauncher)
        hbox.addWidget(self.removeButton)

        self.addButton = QtWidgets.QPushButton("Add")
        self.addButton.clicked.connect(self.addLauncher)
        hbox.addWidget(self.addButton)

        hbox.addStretch(1)

        self.setLayout(mainLayout)

        self.manageLauncherAct = \
            QtGui.QAction(
                QtGui.QIcon(os.path.join("Resources", "images", "settings")),
                "Manage Launchers", self, statusTip="Manage Launchers",
                triggered=self.showMe.emit)

        self.launcherMenu = QtWidgets.QMenu("Launch External...")
        self.loadExternalLaunchers()

    def removeLauncher(self):
        path = self.listWidget.currentItem().text()
        del self.externalLaunchList[path]
        self.loadExternalLaunchers()

    def addLauncher(self):
        path = self.pathLine.text().strip()
        if path != '':
            if os.path.exists(path):
                if path not in self.externalLaunchList:
                    self.externalLaunchList[
                        path] = self.parametersLine.text().strip()
                    self.loadExternalLaunchers()
                else:
                    message = QtWidgets.QMessageBox.warning(
                        self, "Add Launcher", "Path already exists in launchers!")
            else:
                message = QtWidgets.QMessageBox.warning(
                    self, "Add Launcher", "Path does not exists!")
        else:
            message = QtWidgets.QMessageBox.warning(
                self, "Add Launcher", "Path cannot be empty!")

    def loadExternalLaunchers(self):
        self.launcherMenu.clear()
        self.listWidget.clear()
        if len(self.externalLaunchList) > 0:
            self.actionGroup = QtGui.QActionGroup(self)
            self.actionGroup.triggered.connect(
                self.launcherActivated)
            for path, param in self.externalLaunchList.items():
                action = QtGui.QAction(Global.iconFromPath(path), path, self)
                self.actionGroup.addAction(action)
                self.launcherMenu.addAction(action)

                item = QtWidgets.QListWidgetItem(Global.iconFromPath(path), path)
                item.setToolTip(path)
                self.listWidget.addItem(item)

            self.launcherMenu.addSeparator()
            self.launcherMenu.addAction(self.manageLauncherAct)
        else:
            self.launcherMenu.addAction(self.manageLauncherAct)

        if len(self.externalLaunchList) == 0:
            self.removeButton.setDisabled(True)
        else:
            self.removeButton.setDisabled(False)

    def launcherActivated(self, action):
        path = action.text()
        param = self.externalLaunchList[path]
        if os.path.exists(path):
            if os.path.isdir(path):
                os.startfile(path)
            else:
                if param == '':
                    os.startfile(path)
                else:
                    process = QtCore.QProcess(self)
                    process.startDetached(path, [param])
        else:
            message = QtWidgets.QMessageBox.warning(self, "Launch",
                                                "Path is not available.")
