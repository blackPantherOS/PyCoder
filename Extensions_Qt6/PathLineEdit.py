import os
from PyQt6 import QtCore, QtGui, QtWidgets


class PathLineEdit(QtWidgets.QLineEdit):

    def __init__(self, parent=None):
        super(PathLineEdit, self).__init__(parent)

        self.setTextMargins(0, 0, 42, 0)

        hbox = QtWidgets.QHBoxLayout()
        self.setLayout(hbox)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)
        hbox.addStretch(1)

        self.fileButton = QtWidgets.QToolButton()
        self.fileButton.setToolTip(_("Insert File Path"))
        self.fileButton.setAutoRaise(True)
        self.fileButton.setIcon(QtGui.QIcon(os.path.join("Resources", "images", "page")))
        self.fileButton.clicked.connect(self.insertFilePath)
        hbox.addWidget(self.fileButton)

        self.dirButton = QtWidgets.QToolButton()
        self.dirButton.setToolTip(_("Insert Directory Path"))
        self.dirButton.setAutoRaise(True)
        self.dirButton.setIcon(QtGui.QIcon(os.path.join("Resources", "images", "folder_closed")))
        self.dirButton.clicked.connect(self.insertDirPath)
        hbox.addWidget(self.dirButton)

    def insertDirPath(self):
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self, QtCore.QDir.homePath())
        if directory:
            self.setText(os.path.normpath(directory))

    def insertFilePath(self):
        fileName = QtWidgets.QFileDialog.getOpenFileName(self,
                                                     "File", QtCore.QDir.homePath(),
                                                     "All Files (*)")[0]
        if fileName:
            self.setText(os.path.normpath(fileName))
