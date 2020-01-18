from PyQt5 import QtCore, QtGui, QtWidgets


class BuildStatusWidget(QtWidgets.QWidget):

    cancel = QtCore.pyqtSignal()

    def __init__(self, app, useData, parent=None):
        QtWidgets.QDialog.__init__(self, parent)

        self.useData = useData
        self.app = app

        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(mainLayout)

        mainLayout.addWidget(QtWidgets.QLabel("Build Started..."))

        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setMaximumHeight(10)
        self.progressBar.setMinimumWidth(100)
        self.progressBar.setStyleSheet("""
                                         QProgressBar {
                                             border: none;
                                             background: transparent;
                                             border-top: 1px solid #6570EA;
                                             border-radius: 0px;
                                         }

                                         QProgressBar::chunk {
                                             background-color: #65B0EA;
                                             width: 15px;
                                         }
                                        """)
        mainLayout.addWidget(self.progressBar)

        self.hide()

    def showBusy(self, busy):
        if busy:
            self.show()
            self.progressBar.setRange(0, 0)
        else:
            self.hide()
            self.progressBar.setRange(0, 1)
            if self.useData.SETTINGS['SoundsEnabled'] == "True":
                self.app.beep()
