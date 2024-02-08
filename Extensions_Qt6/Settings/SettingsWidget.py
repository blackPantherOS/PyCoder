from PyQt6 import QtCore, QtGui, QtWidgets

from Extensions_Qt6.Settings.ColorScheme.ColorScheme import ColorScheme
from Extensions_Qt6.Settings.Keymap import Keymap
from Extensions_Qt6.Settings.SnippetsManager import SnippetsManager
from Extensions_Qt6.Settings.GeneralSettings import GeneralSettings
from Extensions_Qt6.Settings.ModuleCompletion import ModuleCompletion


class SettingsWidget(QtWidgets.QDialog):

    def __init__(self, useData, mainApp, projectWindowStack, libraryViewer, parent=None):
        QtWidgets.QDialog.__init__(self, parent, QtCore.Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle("Settings")

        self.useData = useData
        self.libraryViewer = libraryViewer
        self.projectWindowStack = projectWindowStack

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(mainLayout)

        self.settingsTab = QtWidgets.QTabWidget()
        self.settingsTab.setObjectName("settingsTab")
        mainLayout.addWidget(self.settingsTab)

        self.generalSettings = GeneralSettings(useData, mainApp, projectWindowStack)
        self.settingsTab.addTab(self.generalSettings, "General")

        self.snippetEditor = SnippetsManager(
            self.useData.appPathDict["snippetsdir"], self)
        self.settingsTab.addTab(self.snippetEditor, "Snippets")

        self.keymapWidget = Keymap(self.useData, projectWindowStack, self)
        self.settingsTab.addTab(self.keymapWidget, "Shortcuts")

        self.colorScheme = ColorScheme(self.useData, projectWindowStack,
                                       libraryViewer)
        self.settingsTab.addTab(self.colorScheme, "Color Scheme")

        self.libraries = ModuleCompletion(self.useData)
        self.settingsTab.addTab(self.libraries, "Module Completion")
