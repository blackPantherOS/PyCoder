import os
from PyQt6 import QtCore, QtGui, QtWidgets


class LibraryAddDialog(QtWidgets.QDialog):

    def __init__(self, editorTabWidget, parent):
        QtWidgets.QDialog.__init__(self, parent, QtCore.Qt.WindowType.Window | QtCore.Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle("Library Add")
        self.setFixedSize(400, 120)

        self.editorTabWidget = editorTabWidget
        self.library = parent

        head = os.path.splitext(self.editorTabWidget.getTabName())[0]

        mainLayout = QtWidgets.QVBoxLayout()

        mainLayout.addWidget(QtWidgets.QLabel("Name in library:"))

        self.nameLine = QtWidgets.QLineEdit()
        self.nameLine.setText(head)
        self.nameLine.selectAll()
        self.nameLine.textChanged.connect(self.textChanged)
        mainLayout.addWidget(self.nameLine)

        hbox = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(hbox)

        self.entireModuleButton = QtWidgets.QRadioButton("Entire Module")
        self.entireModuleButton.setChecked(True)
        hbox.addWidget(self.entireModuleButton)

        self.selectionButton = QtWidgets.QRadioButton("Selection Only")
        if self.editorTabWidget.focusedEditor().selectedText().strip() == '':
            self.selectionButton.setDisabled(True)
        hbox.addWidget(self.selectionButton)
        
        hbox.addStretch(1)
        
        self.showDetailsButton = QtWidgets.QToolButton()
        self.showDetailsButton.setAutoRaise(True)
        self.showDetailsButton.setToolButtonStyle(2)
        self.showDetailsButton.setText("Comments")
        self.showDetailsButton.setIcon(QtGui.QIcon(
            os.path.join("Resources", "images", "extender-down")))
        self.showDetailsButton.clicked.connect(self.showComments)
        hbox.addWidget(self.showDetailsButton)

        self.moreWidget = QtWidgets.QWidget()
        vbox = QtWidgets.QVBoxLayout()
        vbox.setContentsMargins(0, 0, 0, 0)

        self.commentEntry = QtWidgets.QPlainTextEdit()
        vbox.addWidget(self.commentEntry)

        self.moreWidget.setLayout(vbox)
        mainLayout.addWidget(self.moreWidget)

        self.moreWidget.hide()

        hbox = QtWidgets.QHBoxLayout()

        hbox.addStretch(1)

        self.okButton = QtWidgets.QPushButton("OK")
        self.okButton.clicked.connect(self.accept)
        hbox.addWidget(self.okButton)

        cancelButton = QtWidgets.QPushButton("Cancel")
        cancelButton.clicked.connect(self.close)
        hbox.addWidget(cancelButton)

        mainLayout.addLayout(hbox)
        self.setLayout(mainLayout)

        self.accepted = False

        self.exec()

    def showComments(self):
        if self.moreWidget.isVisible():
            self.moreWidget.hide()
            self.setFixedSize(400, 120)
            self.showDetailsButton.setIcon(QtGui.QIcon(
                os.path.join("Resources", "images", "extender-down")))
        else:
            self.moreWidget.show()
            self.setFixedSize(400, 300)
            self.showDetailsButton.setIcon(QtGui.QIcon(
                os.path.join("Resources", "images", "extender-up")))

    def textChanged(self):
        if self.nameLine.text().strip() == '':
            self.okButton.setDisabled(True)
        else:
            self.okButton.setDisabled(False)

    def accept(self):
        self.accepted = True

        file_name = self.nameLine.text().strip()
        self.name = os.path.splitext(file_name)[0]

        self.close()
