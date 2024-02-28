import os
from PyQt6 import QtCore, QtGui, QtWidgets


class MessagesWidget(QtWidgets.QTreeWidget):

    def __init__(self, bottomStackSwitcher, vSplitter, parent=None):
        QtWidgets.QTreeWidget.__init__(self, parent)

        self.bottomStackSwitcher = bottomStackSwitcher
        self.vSplitter = vSplitter

        self.setHeaderLabels([_("Message"), _("Time")])
        self.setColumnWidth(0, 400)
        self.setColumnWidth(1, 40)

    def addMessage(self, messType, title, messageList):
        parentItem = QtWidgets.QTreeWidgetItem(self)
        if messType == 0:
            parentItem.setIcon(0, QtGui.QIcon(
                os.path.join("Resources", "images", "security", "attention")))
        elif messType == 1:
            parentItem.setIcon(0, QtGui.QIcon(
                os.path.join("Resources", "images", "security", "warning")))
        elif messType == 2:
            parentItem.setIcon(0, QtGui.QIcon(
                os.path.join("Resources", "images", "security", "danger")))
        parentItem.setText(0, title)
        parentItem.setText(1, QtCore.QDateTime().currentDateTime().toString())
        for i in messageList:
            item = QtWidgets.QTreeWidgetItem(parentItem)
            item.setFirstColumnSpanned(True)
            item.setText(0, i)
            parentItem.addChild(item)
        parentItem.setExpanded(True)
        #self.scrollToItem(parentItem, 1)
        self.scrollToItem(parentItem, QtWidgets.QAbstractItemView.ScrollHint.EnsureVisible)


        self.vSplitter.showMessageAvailable()
        self.bottomStackSwitcher.setCount(self, str(self.topLevelItemCount()))
        self.bottomStackSwitcher.setCurrentWidget(self)
