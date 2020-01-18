import os

from PyQt5 import QtGui, QtWidgets


class GotoLineWidget(QtWidgets.QLabel):

    def __init__(self, editorTabWidget, parent=None):
        QtWidgets.QLabel.__init__(self, parent=None)

        self.editorTabWidget = editorTabWidget

        self.setMinimumHeight(35)
        self.setMaximumHeight(35)
        self.setMinimumWidth(200)
        self.setMaximumWidth(200)

        self.gotoLineAct = \
            QtWidgets.QAction(
                QtGui.QIcon(os.path.join("Resources", "images", "mail_check")),
                "Goto Line", self, statusTip="Goto Line",
                triggered=self.gotoLine)

        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.setContentsMargins(3, 3, 3, 3)
        mainLayout.setSpacing(2)
        self.setLayout(mainLayout)

        self.hideButton = QtWidgets.QToolButton()
        self.hideButton.setAutoRaise(True)
        self.hideButton.setIcon(
            QtGui.QIcon(os.path.join("Resources", "images", "exit")))
        self.hideButton.clicked.connect(self.hide)
        mainLayout.addWidget(self.hideButton)

        self.lineNumberLine = QtWidgets.QSpinBox()
        self.lineNumberLine.setMinimumHeight(25)
        self.lineNumberLine.setMinimum(1)
        self.lineNumberLine.setMaximum(100000000)
        self.lineNumberLine.valueChanged.connect(self.gotoLine)
        mainLayout.addWidget(self.lineNumberLine)

        self.goButton = QtWidgets.QToolButton()
        self.goButton.setAutoRaise(True)
        self.goButton.setDefaultAction(self.gotoLineAct)
        mainLayout.addWidget(self.goButton)

        mainLayout.setStretch(1, 1)

        self.setStyleSheet("""
                            QLabel {
                                background: rgba(138, 201, 255, 200);
                                border-radius: 0px;
                            }
                             """)

    def gotoLine(self, lineno):
        if lineno is False:
            lineno = self.lineNumberLine.value()
        self.editorTabWidget.focusedEditor().showLine(lineno - 1)
