import os

from PyQt5 import QtCore, QtGui, QtWidgets

from Xtra import autopep8
from Xtra import pep8
import pyflakes
import rope
import cx_Freeze


class About(QtWidgets.QDialog):

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent,
                               QtCore.Qt.Window | QtCore.Qt.WindowCloseButtonHint)

        self.setWindowTitle("About")

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(mainLayout)

        self.setFixedSize(500, 300)

        form = QtWidgets.QFormLayout()
        #form.setMargin(10)
        form.addRow("<b>Version</b>", QtWidgets.QLabel("0.1.1"))
        form.addRow("<b>Author</b>", QtWidgets.QLabel("blackPanther Project"))
        form.addRow("<b>Email</b>", QtWidgets.QLabel("info@blackpanther.hu"))

        mainLayout.addLayout(form)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(5, 0, 5, 0)
        mainLayout.addLayout(hbox)

        self.label = QtWidgets.QLabel("External Libraries:")
        hbox.addWidget(self.label)

        hbox.addStretch(1)

        licenseButton = QtWidgets.QPushButton("License")
        licenseButton.setCheckable(True)
        licenseButton.clicked.connect(self.showLicense)
        hbox.addWidget(licenseButton)

        self.view = QtWidgets.QStackedWidget()
        mainLayout.addWidget(self.view)

        table = QtWidgets.QTreeWidget()
        table.setMinimumHeight(150)
        table.setIndentation(0)
        table.setHeaderLabels(["Name", "Version", "Author"])
        table.setColumnWidth(0, 150)
        table.addTopLevelItem(QtWidgets.QTreeWidgetItem(
            ["Rope", rope.VERSION, "Ali Gholami Rudi"]))
        table.addTopLevelItem(QtWidgets.QTreeWidgetItem(
            ["PyFlakes", pyflakes.__version__, "Florent Xicluna"]))
        table.addTopLevelItem(QtWidgets.QTreeWidgetItem(
            ["Pep8", pep8.__version__, "Florent Xicluna"]))
        table.addTopLevelItem(QtWidgets.QTreeWidgetItem(
            ["PyQt5", "4.10", "Riverbank Computing Limited"]))
        table.addTopLevelItem(QtWidgets.QTreeWidgetItem(
            ["AutoPep8", autopep8.__version__, "Hideo Hattori"]))
        table.addTopLevelItem(QtWidgets.QTreeWidgetItem(
            ["CxFreeze", cx_Freeze.version, "Anthony Tuininga"]))
        self.view.addWidget(table)

        self.licenseEdit = QtWidgets.QTextEdit()
        file = open(os.path.join("Resources", "LICENSE"), "r")
        self.licenseEdit.setText(file.read())
        file.close()

        self.view.addWidget(self.licenseEdit)

        self.hide()

    def showLicense(self, checked):
        if checked:
            self.view.setCurrentIndex(1)
            self.label.hide()
        else:
            self.view.setCurrentIndex(0)
            self.label.show()
