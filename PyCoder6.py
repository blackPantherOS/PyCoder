#!/usr/bin/python3
#*********************************************************************************************************
#*   __     __               __     ______                __   __                      _______ _______   *
#*  |  |--.|  |.---.-..----.|  |--.|   __ \.---.-..-----.|  |_|  |--..-----..----.    |       |     __|  *
#*  |  _  ||  ||  _  ||  __||    < |    __/|  _  ||     ||   _|     ||  -__||   _|    |   -   |__     |  *
#*  |_____||__||___._||____||__|__||___|   |___._||__|__||____|__|__||_____||__|      |_______|_______|  *
#* http://www.blackpantheros.eu | http://www.blackpanther.hu - kbarcza[]blackpanther.hu * Charles Barcza *
#*************************************************************************************(c)2002-2020********
# Project         : PyCoder
# Module          : Development IDE
# File            : PyCoder.py
# Version         : 0.5.0
# Authors         : Charles K. Barcza & Miklos Horvath - info@blackpanther.hu
# Created On      : Fri Jan 17 2020
# Last updated    : Fri Jan 26 2024
# Credits         : Harrison Amoatey - the Qt4 code
# Purpose         : LightWare Python IDE based on Qt6
#---------------------------------------------------------------

import sys
import os
import logging

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QPoint

from Extensions_Qt6.UseData import UseData
from Extensions_Qt6.Library.Library import Library
from Extensions_Qt6.About import About
from Extensions_Qt6.Settings.SettingsWidget import SettingsWidget
from Extensions_Qt6.Projects.Projects import Projects
from Extensions_Qt6.BusyWidget import BusyWidget
from Extensions_Qt6 import StyleSheet
from Extensions_Qt6.Start import Start
from Extensions_Qt6.StackSwitcher import StackSwitcher


class PyCoder(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowIcon(QtGui.QIcon(os.path.join(
        "Resources", "images", "Icon")))
        self.setWindowTitle("PyCoder - Loading...")

        screen = QtWidgets.QApplication.primaryScreen().geometry()
        self.resize(screen.width() - 200, screen.height() - 200)
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height()
        - size.height()) // 2)
        self.lastWindowGeometry = self.geometry()

        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setSpacing(0)
        mainLayout.setContentsMargins(0, 0, 0, 0)

        self.useData = UseData()

        logging.basicConfig(format=
        '%(asctime)s - %(levelname)s - %(message)s',
                            filename=self.useData.appPathDict["logfile"],
                            level=logging.DEBUG)
        if sys.version_info.major < 3:
            logging.error("This application requires Python 3")
            sys.exit(1)

        self.library = Library(self.useData)
        self.busyWidget = BusyWidget(app, self.useData, self)

        if self.useData.SETTINGS["UI"] == "Custom":
            app.setStyleSheet(StyleSheet.globalStyle)

        self.projectWindowStack = QtWidgets.QStackedWidget()

        self.projectTitleBox = QtWidgets.QComboBox()
        self.projectTitleBox.setMinimumWidth(180)
        self.projectTitleBox.setStyleSheet(StyleSheet.projectTitleBoxStyle)
        self.projectTitleBox.setItemDelegate(QtWidgets.QStyledItemDelegate())
        self.projectTitleBox.currentIndexChanged.connect(self.projectChanged)
        self.projectTitleBox.activated.connect(self.projectChanged)

        self.settingsWidget = SettingsWidget(self.useData, app,
                                             self.projectWindowStack, 
                                             self.library.codeViewer, self)
        self.settingsWidget.colorScheme.styleEditor(self.library.codeViewer)

        startWindow = Start(self.useData, self)
        self.addProject(startWindow, "Start",
                        "Start", os.path.join(
                        "Resources", "images", "flag-green"))

        self.projects = Projects(self.useData, self.busyWidget,
                                 self.library, self.settingsWidget, app,
                                 self.projectWindowStack, 
                                 self.projectTitleBox, self)

        self.createActions()

        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(5, 3, 5, 3)
        mainLayout.addLayout(hbox)

        hbox.addStretch(1)

        self.pagesStack = QtWidgets.QStackedWidget()
        mainLayout.addWidget(self.pagesStack)

        self.projectSwitcher = StackSwitcher(self.pagesStack)
        self.projectSwitcher.setStyleSheet(StyleSheet.mainMenuStyle)
        hbox.addWidget(self.projectSwitcher)

        self.addPage(self.projectWindowStack, "EDITOR", QtGui.QIcon(
            os.path.join("Resources", "images", "hire-me")))

        self.addPage(self.library, "LIBRARY", QtGui.QIcon(
            os.path.join("Resources", "images", "library")))
        self.projectSwitcher.setDefault()

        hbox.addWidget(self.projectTitleBox)
        hbox.setSpacing(5)

        self.settingsButton = QtWidgets.QToolButton()
        self.settingsButton.setAutoRaise(True)
        self.settingsButton.setDefaultAction(self.settingsAct)
        hbox.addWidget(self.settingsButton)

        self.fullScreenButton = QtWidgets.QToolButton()
        self.fullScreenButton.setAutoRaise(True)
        self.fullScreenButton.setDefaultAction(self.showFullScreenAct)
        hbox.addWidget(self.fullScreenButton)

        self.aboutButton = QtWidgets.QToolButton()
        self.aboutButton.setAutoRaise(True)
        self.aboutButton.setDefaultAction(self.aboutAct)
        hbox.addWidget(self.aboutButton)

        self.setKeymap()

        if self.useData.settings["firstRun"] == 'True':
            self.showMaximized()
        else:
            self.restoreUiState()

        self.useData.settings["running"] = 'True'
        self.useData.settings["firstRun"] = 'False'
        self.useData.saveSettings()

    def createActions(self):
        self.aboutAct = QtGui.QAction(
            QtGui.QIcon(os.path.join("Resources", "images", "properties")),
            "About PyCoder", self, statusTip="About PyCoder",
            triggered=self.showAbout)

        self.showFullScreenAct = \
            QtGui.QAction(
                QtGui.QIcon(os.path.join(
                "Resources", "images", "Fullscreen")),
                "Fullscreen", self,
                statusTip="Fullscreen",
                          triggered=self.showFullScreenMode)

        self.settingsAct = QtGui.QAction(
            QtGui.QIcon(os.path.join("Resources", "images", "config")),
            "Settings", self,
            statusTip="Settings", triggered=self.showSettings)

    def addPage(self, pageWidget, name, iconPath):
        self.projectSwitcher.addButton(name=name, icon=iconPath)
        self.pagesStack.addWidget(pageWidget)

    def loadProject(self, path, show=False, new=False):
        self.projects.loadProject(path, show, new)

    def newProject(self):
        self.projects.newProjectDialog.exec()

    def showProject(self, path):
        if not os.path.exists(path):
            message = QtWidgets.QMessageBox.warning(
                self, "Open Project", "Project cannot be be found!")
        else:
            if path in self.useData.OPENED_PROJECTS:
                for i in range(self.projectWindowStack.count() - 1):
                    window = self.projectWindowStack.widget(i)
                    p_path = window.projectPathDict["root"]
                    if os.path.samefile(path, p_path):
                        self.projectTitleBox.setCurrentIndex(i)
                        return True
        return False

    def addProject(self, window, name, type='Project', iconPath=None):
        self.projectWindowStack.insertWidget(0, window)
        if type == 'Project':
            self.projectTitleBox.insertItem(0, QtGui.QIcon(
                os.path.join("Resources", "images", "project")),
                name, [window, type])
        else:
            self.projectTitleBox.insertItem(0, QtGui.QIcon(
                iconPath), name, [window, type])

    def projectChanged(self, index):
        data = self.projectTitleBox.itemData(index)
        window = data[0]
        windowType = data[1]
        if windowType == "Start":
            self.setWindowTitle("PyCoder - Start")
        elif windowType == "Project":
            title = window.editorTabWidget.getEditorData("filePath")
            self.updateWindowTitle(title)
        self.projectWindowStack.setCurrentWidget(window)

    def removeProject(self, window):
        for index in range(self.projectTitleBox.count() - 1):
            data = self.projectTitleBox.itemData(index)
            windowWidget = data[0]
            if windowWidget == window:
                self.projectWindowStack.removeWidget(window)
                self.projectTitleBox.removeItem(index)

    def updateWindowTitle(self, title):
        if title is None:
            title = "PyCoder - " + "Unsaved"
        else:
            window = self.projectTitleBox.itemData(
                self.projectTitleBox.currentIndex())[0]
            if title.startswith(window.projectPathDict["sourcedir"]):
                src_dir = window.projectPathDict["sourcedir"]
                n = title.partition(src_dir)[-1]
                title = 'PyCoder - ' + n
            else:
                title = "PyCoder - " + title
        self.setWindowTitle(title)

    def showAbout(self):
        aboutPane = About(self)
        aboutPane.exec()

    def showSettings(self):
        self.settingsWidget.show()

    def showFullScreenMode(self):
        if self.isFullScreen():
            self.showNormal()
            self.setGeometry(self.lastWindowGeometry)
        else:
            # get current size ahd show Fullscreen
            # so we can later restore to proper position
            self.lastWindowGeometry = self.geometry()
            self.showFullScreen()

    def saveUiState(self):
        settings = QtCore.QSettings("PyCoder", "config")
        settings.beginGroup("MainWindow")
        settings.setValue("geometry", self.geometry())
        settings.setValue("lsplitter", self.library.mainSplitter.saveState())
        settings.setValue(
        "snippetsMainsplitter", 
        self.settingsWidget.snippetEditor.mainSplitter.saveState())
        settings.setValue("windowMaximized", self.isMaximized())
        settings.endGroup()

    def restoreUiState(self):
        settings = QtCore.QSettings("PyCoder", "config")
        settings.beginGroup("MainWindow")
        if settings.value("windowMaximized", True, type=bool):
            self.showMaximized()
        else:
            self.setGeometry(settings.value("geometry"))
            self.show()
        self.library.mainSplitter.restoreState(settings.value("lsplitter"))
        self.settingsWidget.snippetEditor.mainSplitter.restoreState(
            settings.value("snippetsMainsplitter"))
        settings.endGroup()

    def closeEvent(self, event):
        for i in range(self.projectWindowStack.count() - 1):
            window = self.projectWindowStack.widget(i)
            closed = window.closeWindow()
            if not closed:
                self.projectTitleBox.setCurrentIndex(i)
                event.ignore()
                return
            else:
                pass
        self.saveUiState()
        self.useData.saveUseData()
        app.closeAllWindows()

        event.accept()

    def setKeymap(self):
        shortcuts = self.useData.CUSTOM_SHORTCUTS

        self.shortFullscreen = QtGui.QShortcut(
            shortcuts["Ide"]["Fullscreen"], self)
        self.shortFullscreen.activated.connect(self.showFullScreenMode)

app = QtWidgets.QApplication(sys.argv)

splash = QtWidgets.QSplashScreen(
    QtGui.QPixmap(os.path.join("Resources", "images", "splash")))
splash.show()

main = PyCoder()

splash.finish(main)

sys.exit(app.exec())
