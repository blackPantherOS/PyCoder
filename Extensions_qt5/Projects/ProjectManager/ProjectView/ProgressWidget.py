import os

from PyQt5 import QtCore, QtGui, QtWidgets


class ProgressWidget(QtWidgets.QLabel):

    updateProgress = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        QtWidgets.QLabel.__init__(self, parent)

        self.setMinimumHeight(25)
        self.setObjectName("mainLabel")

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setSpacing(0)
        mainLayout.setContentsMargins(2, 2, 2, 2)
        self.setLayout(mainLayout)
        
        self.progressBar = QtWidgets.QProgressBar()
        self.progressBar.setTextVisible(False)
        self.progressBar.setRange(0, 100)
        self.updateProgress.connect(self.updateValue)
        mainLayout.addWidget(self.progressBar)
        

        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(2, 2, 2, 2)
        hbox.setSpacing(0)
        self.progressBar.setLayout(hbox)

        hbox.addWidget(QtWidgets.QLabel("Copying: "))

        self.captionLabel = QtWidgets.QLabel()
        self.captionLabel.setStyleSheet("""
                                          QLabel  {
                                              color: #003366;
                                          }
                                        """)
        hbox.addWidget(self.captionLabel)

        hbox.addStretch(1)

        self.cancelButton = QtWidgets.QToolButton()
        self.cancelButton.setIcon(
            QtGui.QIcon(os.path.join("Resources", "images", "cross")))
        hbox.addWidget(self.cancelButton)

        self.setStyleSheet("""
                              QLabel#mainLabel  {
                                  background: #ffffff;
                                  border: none;
                              }

                              QProgressBar {
                                 border: None;
                                 text-align: center;
                                 padding: 0px;
                                 border-radius: 0px;
                                 background-color: Transparent;
                             }

                             QProgressBar::chunk {
                                  color: black;
                                  border-radius: 0px;
                                  background-color: #EDEDED;
                             }

                            """)

    def reset(self):
        self.progressBar.setValue(0)

    def updateCurrentJob(self, job):
        self.captionLabel.setText(job)

    def updateValue(self, newValue):
        self.progressBar.setValue(newValue)

    def showBusy(self, show, mess=None):
        if show:
            self.captionLabel.setText(mess)
            self.cancelButton.show()
            self.show()
        else:
            self.hide()
            self.reset()
