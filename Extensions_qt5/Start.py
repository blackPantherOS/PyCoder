import os
from PyQt5 import QtCore, QtGui, QtWidgets


class Start(QtWidgets.QLabel):

    def __init__(self, useData,  parent):
        QtWidgets.QLabel.__init__(self)

        self.pycoder = parent
        self.useData = useData

        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setScaledContents(True)
        self.setObjectName("mainlabel")
        self.setLayout(mainLayout)

        mainLayout.addStretch(1)

        vbox = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(vbox)

        vbox.addStretch(1)

        centerLabel = QtWidgets.QLabel()
        centerLabel.setObjectName("centerlabel")
        centerLabel.setMinimumWidth(500)
        centerLabel.setMinimumHeight(300)
        centerLabel.setScaledContents(True)
        centerLabel.setStyleSheet("""
                            QListView {
                                 show-decoration-selected: 1; /* make the selection span the entire width of the view */
                                 border: none;
                            }

                            QListView::item {
                                 min-height: 20px;
                            }

                            QListView::item:hover {
                                 border: none;
                                 background: #E3E3E3;
                            }

                            QListView::item:selected:!active {
                                 border: 1px solid white;
                                 background: #E3E3E3;
                            }

                            QListView::item:selected:active {
                                 color: white;
                                 background: #3F3F3F;
                            }""")
        vbox.addWidget(centerLabel)

        vbox.addStretch(2)

        shadowEffect = QtWidgets.QGraphicsDropShadowEffect()
        shadowEffect.setColor(QtGui.QColor("#000000"))
        shadowEffect.setXOffset(0)
        shadowEffect.setYOffset(0)
        shadowEffect.setBlurRadius(20)
        centerLabel.setGraphicsEffect(shadowEffect)

        centralLayout = QtWidgets.QVBoxLayout()
        centerLabel.setLayout(centralLayout)

        hbox = QtWidgets.QHBoxLayout()
        centralLayout.addLayout(hbox)

        label = QtWidgets.QLabel("Getting started...")
        label.setFont(QtGui.QFont("Consolas", 20))
        hbox.addWidget(label)

        hbox.addStretch(1)

        label = QtWidgets.QLabel()
        label.setScaledContents(True)
        label.setMaximumWidth(35)
        label.setMinimumWidth(35)
        label.setMaximumHeight(35)
        label.setMinimumHeight(35)
        label.setPixmap(QtGui.QPixmap(os.path.join("Resources", "images", "compass")))
        hbox.addWidget(label)

        frame = QtWidgets.QFrame()
        frame.setGeometry(1, 1, 1, 1)
        frame.setFrameShape(frame.HLine)
        frame.setFrameShadow(frame.Plain)
        centralLayout.addWidget(frame)

        label = QtWidgets.QLabel(
            "For the sake of convenience, most tasks are handled in the "
            "context of a project. Start editing your files by first "
            "creating a project or opening an existing one.")
        label.setWordWrap(True)
        label.setFont(QtGui.QFont("Consolas", 10))
        centralLayout.addWidget(label)

        centralLayout.addStretch(1)

        label = QtWidgets.QLabel("Recent Projects:")
        label.setStyleSheet("color: #0063A6; font: 12px;")
        centralLayout.addWidget(label)

        self.recentProjectsListWidget = QtWidgets.QListWidget()
        for i in useData.OPENED_PROJECTS:
            self.recentProjectsListWidget.addItem(QtWidgets.QListWidgetItem(i))
        self.recentProjectsListWidget.itemDoubleClicked.connect(
            self.openProjectFromList)
        centralLayout.addWidget(self.recentProjectsListWidget)

        frame = QtWidgets.QFrame()
        frame.setGeometry(1, 1, 1, 1)
        frame.setFrameShape(frame.HLine)
        frame.setFrameShadow(frame.Plain)
        centralLayout.addWidget(frame)

        hbox = QtWidgets.QHBoxLayout()
        centralLayout.addLayout(hbox)

        newButton = QtWidgets.QPushButton("New Project")
        newButton.setIcon(QtGui.QIcon(os.path.join("Resources", "images", "inbox--plus")))
        newButton.clicked.connect(self.createProject)
        hbox.addWidget(newButton)

        openButton = QtWidgets.QPushButton("Open Project")
        openButton.setIcon(QtGui.QIcon(os.path.join("Resources", "images", "wooden-box")))
        openButton.clicked.connect(self.openProject)
        hbox.addWidget(openButton)

        hbox.addStretch(1)

        homePageButton = QtWidgets.QPushButton("Project Homepage")
        homePageButton.setIcon(QtGui.QIcon(os.path.join("Resources", "images", "Web")))
        homePageButton.clicked.connect(self.visitHomepage)
        hbox.addWidget(homePageButton)

        mainLayout.addStretch(1)

        style = """
            QLabel#mainlabel {background: #565656;
                    }

            QLabel#centerlabel {border-radius: 2px;
                background: #FFFFFF;
                     }

            QPushButton {min-width: 105;}
            """

        self.setStyleSheet(style)

    def visitHomepage(self):
        QtGui.QDesktopServices().openUrl(QtCore.QUrl(
            """https://www.blackPanther.hu"""))

    def createProject(self):
        self.pycoder.newProject()

    def openProject(self):
        options = QtWidgets.QFileDialog.DontResolveSymlinks | QtWidgets.QFileDialog.ShowDirsOnly
        directory = QtWidgets.QFileDialog.getExistingDirectory(self,
                                                           "Project Folder", self.useData.getLastOpenedDir(), options)
        if directory:
            directory = os.path.normpath(directory)
            self.useData.saveLastOpenedDir(directory)
            self.pycoder.loadProject(directory, True)

    def openProjectFromList(self, item):
        self.pycoder.loadProject(item.text(), True)
