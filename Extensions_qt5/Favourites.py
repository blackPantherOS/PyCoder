import os
from PyQt5 import QtCore, QtGui, QtWidgets

from Extensions_qt5 import StyleSheet


class Favourites(QtWidgets.QLabel):

    showMe = QtCore.pyqtSignal()

    openFile = QtCore.pyqtSignal(str)

    def __init__(self, favouritesList, messagesWidget, parent=None):
        super(Favourites, self).__init__(parent)

        self.setMinimumSize(600, 230)
        self.setObjectName("containerLabel")
        self.setStyleSheet(StyleSheet.toolWidgetStyle)

        self.setBackgroundRole(QtGui.QPalette.Background)
        self.setAutoFillBackground(True)

        self.messagesWidget = messagesWidget
        self.favouritesList = favouritesList

        self.manageFavAct = \
            QtWidgets.QAction(
                QtGui.QIcon(os.path.join("Resources", "images", "settings")),
                          "Manage Favourites", self, statusTip="Manage Favourites",
                          triggered=self.showMe.emit)

        mainLayout = QtWidgets.QVBoxLayout()

        hbox = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(hbox)

        label = QtWidgets.QLabel("Manage Favourites")
        label.setObjectName("toolWidgetNameLabel")
        hbox.addWidget(label)

        hbox.addStretch(1)

        self.hideButton = QtWidgets.QToolButton()
        self.hideButton.setAutoRaise(True)
        self.hideButton.setIcon(
            QtGui.QIcon(os.path.join("Resources", "images", "cross_")))
        self.hideButton.clicked.connect(self.hide)
        hbox.addWidget(self.hideButton)

        self.favouritesListWidget = QtWidgets.QListWidget()
        mainLayout.addWidget(self.favouritesListWidget)

        hbox = QtWidgets.QHBoxLayout()

        self.removeButton = QtWidgets.QPushButton("Remove")
        self.removeButton.clicked.connect(self.removeFavourite)
        hbox.addWidget(self.removeButton)

        hbox.addStretch(1)

        mainLayout.addLayout(hbox)

        self.setLayout(mainLayout)

        self.favouritesMenu = QtWidgets.QMenu("Favourites")
        self.favouritesMenu.setIcon(QtGui.QIcon(
            os.path.join("Resources", "images", "bookmarked_url")))
        self.loadFavourites()

    def removeFavourite(self):
        row = self.favouritesListWidget.currentRow()
        del self.favouritesList[row]
        self.loadFavourites()

    def addToFavourites(self, path):
        if path in self.favouritesList:
            pass
        else:
            self.favouritesList.append(path)
            self.favouritesList.sort()
            self.loadFavourites()
            self.messagesWidget.addMessage(0, "Favourites",
                                           ["'{0}' added!".format(path)])

    def loadFavourites(self):
        self.favouritesMenu.clear()
        self.favouritesListWidget.clear()
        if len(self.favouritesList) > 0:
            self.favouritesActionGroup = QtWidgets.QActionGroup(self)
            self.favouritesActionGroup.triggered.connect(
                self.favouriteActivated)
            for i in self.favouritesList:
                action = QtWidgets.QAction(QtGui.QIcon(
                    os.path.join("Resources", "images", "star")), i, self)
                self.favouritesActionGroup.addAction(action)
                self.favouritesMenu.addAction(action)

                item = QtWidgets.QListWidgetItem(i.strip())
                item.setToolTip(i)
                item.setSizeHint(QtCore.QSize(20, 20))
                self.favouritesListWidget.addItem(item)

            self.favouritesMenu.addSeparator()
            self.favouritesMenu.addAction(self.manageFavAct)
            self.removeButton.setDisabled(False)
        else:
            action = QtWidgets.QAction("No Favourites", self)
            self.favouritesMenu.addAction(action)
            self.favouritesMenu.addAction(action)
            self.removeButton.setDisabled(True)

    def favouriteActivated(self, action):
        path = action.text()
        if os.path.exists(path):
            self.openFile.emit(path)
        else:
            message = QtWidgets.QMessageBox.warning(self, "Open",
                                                "File is no longer available.")
