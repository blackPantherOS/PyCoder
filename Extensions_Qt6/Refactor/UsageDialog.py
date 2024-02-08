import os
from PyQt6 import QtCore, QtGui, QtWidgets


class UsageDialog(QtWidgets.QDialog):

    def __init__(self, editorTabWidget, title, itemsList, parent=None):
        QtWidgets.QDialog.__init__(self, parent, QtCore.Qt.WindowType.Window |
                               QtCore.Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle(title)
        self.resize(600, 300)

        self.editorTabWidget = editorTabWidget

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(mainLayout)

        self.view = QtWidgets.QTreeWidget()
        self.view.setHeaderLabels(["#"])
        self.view.setColumnWidth(0, 300)
        self.view.setSortingEnabled(True)
        self.view.sortByColumn(0, QtCore.Qt.SortOrder.AscendingOrder)
        self.view.itemActivated.connect(self.showLine)
        mainLayout.addWidget(self.view)

        for item in itemsList:
            self.view.addTopLevelItem(item)

        self.exec_()

    def showLine(self, item):
        if item.parent() is None:
            return
        path = item.parent().text(0)
        fullPath = os.path.join(
            self.editorTabWidget.projectPathDict["sourcedir"], path)
        self.editorTabWidget.loadfile(fullPath)
        line = int(item.text(0)) - 1
        self.editorTabWidget.showLine(line)
