import os

from PyQt6 import QtCore, QtGui, QtWidgets

try:
    import autopep8
except:
    from Xtra import autopep8

try:
    import pycodestyle
except:
    from Xtra import pycodestyle

import pyflakes
import rope
import cx_Freeze

class About(QtWidgets.QDialog):

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent,
                               QtCore.Qt.WindowType.Window | QtCore.Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle(_("About"))

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(mainLayout)

        self.setFixedSize(500, 350)
        form = QtWidgets.QFormLayout()
        form.setContentsMargins(10, 10, 10, 10)
        form.addRow(_("<b>Version</b>"), QtWidgets.QLabel("0.6.0"))
        form.addRow(_("<b>Author</b>"), QtWidgets.QLabel("blackPanther Project"))
        form.addRow(_("<b>Email</b>"), QtWidgets.QLabel("info@blackpanther.hu"))

        mainLayout.addLayout(form)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(5, 0, 5, 0)
        mainLayout.addLayout(hbox)

        self.label = QtWidgets.QLabel(_("External Libraries:"))
        hbox.addWidget(self.label)

        hbox.addStretch(1)

        licenseButton = QtWidgets.QPushButton(_("License"))
        licenseButton.setCheckable(True)
        licenseButton.clicked.connect(self.showLicense)
        hbox.addWidget(licenseButton)

        self.view = QtWidgets.QStackedWidget()
        mainLayout.addWidget(self.view)

        table = QtWidgets.QTreeWidget()
        table.setMinimumHeight(150)
        table.setIndentation(0)
        table.setHeaderLabels([_("Name"), _("Version"), _("Author")])
        table.setColumnWidth(0, 150)
        table.addTopLevelItem(QtWidgets.QTreeWidgetItem(
            ["Rope", rope.VERSION, "Ali Gholami Rudi"]))
        table.addTopLevelItem(QtWidgets.QTreeWidgetItem(
            ["PyFlakes", pyflakes.__version__, "Florent Xicluna"]))
        table.addTopLevelItem(QtWidgets.QTreeWidgetItem(
            ["PyCodeStyle (Pep8)", pycodestyle.__version__, "Florent Xicluna, Ian Lee"]))
        table.addTopLevelItem(QtWidgets.QTreeWidgetItem(
            ["PyQt6", "4.10", "Riverbank Computing Limited"]))
        table.addTopLevelItem(QtWidgets.QTreeWidgetItem(
            ["AutoPep8", autopep8.__version__, "Hideo Hattori"]))
        table.addTopLevelItem(QtWidgets.QTreeWidgetItem(
            ["CxFreeze", cx_Freeze.__version__, "Anthony Tuininga"]))
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
