from PyQt6 import QtCore, QtGui, QtWidgets


class BusyWidget(QtWidgets.QDialog):

    cancel = QtCore.pyqtSignal()

    def __init__(self, app, useData, parent=None):
        super().__init__(parent, flags=QtCore.Qt.WindowType.Window)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground, True)

        self.setFixedSize(250, 60)

        self.app = app
        self.useData = useData

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.setSpacing(0)
        self.setLayout(mainLayout)

        mainLabel = QtWidgets.QLabel()
        mainLabel.setStyleSheet(
            """background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                                 stop: 0 #343434,
                                                 stop: 0.7 #343434);

                                border: 1px solid #C9EAFB;
                                border-radius: 0px;
                            """)
        mainLayout.addWidget(mainLabel)

        vbox = QtWidgets.QVBoxLayout()
        mainLabel.setLayout(vbox)

        self.captionLabel = QtWidgets.QLabel()
        self.captionLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        self.captionLabel.setStyleSheet(
            "color: white; background: none; border: none;")
        vbox.addWidget(self.captionLabel)
        vbox.addStretch(1)

        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setMaximumHeight(15)
        self.progressBar.setStyleSheet(
            """
                          QProgressBar {
                             border: 1px solid #707070;
                             text-align: center;
                             font-size: 10px;
                             padding: 1px;
                             border-radius: 0px;
                             background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                       stop:0 #333333, stop:1 #666666);
                         }

                         QProgressBar::chunk {
                              color: black;
                              border-radius: 0px;
                              background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                       stop:0 #95c4f0, stop:1 #5d7a96);
                         }

                    """
            )
        self.progressBar.setRange(0, 0)
        vbox.addWidget(self.progressBar)

        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        vbox.addLayout(hbox)

        self.cancelButton = QtWidgets.QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.stop)
        self.cancelButton.setStyleSheet("""
                    QPushButton {
                        color: white;
                        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6B6B6B,stop: 0.3 #636363,stop: 1 #525252);
                        border-radius: 0px;
                        border: 1px solid 1E1E1E;
                    }

                    QPushButton:hover {
                        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #878787,stop: 0.3 #787878,stop: 1 #5C5C5C);
                    }

                    QPushButton:pressed {
                        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #3E3E3E,stop: 1 #353535);
                        padding-top: 1px;
                    }
                            """)
        hbox.addWidget(self.cancelButton)

        hbox.addStretch(1)

    def keyPressEvent(self, event):
        event.ignore()

    def stop(self):
        self.cancel.emit()

    def showBusy(self, show, mess=None, enableCancel=False):
        if show:
            self.progressBar.setRange(0, 0)
            self.captionLabel.setText(mess)
            if enableCancel:
                self.setFixedSize(250, 75)
                self.cancelButton.show()
            else:
                self.cancelButton.hide()
                self.setFixedSize(250, 60)
            self.exec()
        else:
            self.progressBar.setRange(1, 1)
            self.hide()
            if self.useData.SETTINGS['SoundsEnabled'] == "True":
                self.app.beep()
