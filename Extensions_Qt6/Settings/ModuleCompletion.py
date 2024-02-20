from PyQt6 import QtCore, QtGui, QtWidgets


class ModuleCompletion(QtWidgets.QTreeWidget):

    def __init__(self, useData, parent=None):
        QtWidgets.QTreeWidget.__init__(self, parent)

        self.useData = useData

        self.setHeaderLabel("Modules")
        for i, v in self.useData.libraryDict.items():
            item = QtWidgets.QTreeWidgetItem(self)
            item.setCheckState(0, QtCore.Qt.CheckState.Checked)
            item.setText(0, i)

            for sub in v[0]:
                subItem = QtWidgets.QTreeWidgetItem(item)
                subItem.setText(0, sub)

        self.createActions()

    def createActions(self):
        self.addItemAct = QtGui.QAction(
            "Add Library", self, statusTip="Add Library", triggered=self.addLibrary)

        self.removeItemAct = \
            QtGui.QAction(
                "Remove Library", self, statusTip="Remove Library", triggered=self.removeLibrary)

        self.addModuleAct = \
            QtGui.QAction(
                "Add Module", self, statusTip="Add Module", triggered=self.addModule)

        self.removeModuleAct = \
            QtGui.QAction(
                "Remove Module", self, statusTip="Remove Module", triggered=self.removeModule)

        self.contextMenu = QtWidgets.QMenu()
        self.contextMenu.addAction(self.addItemAct)
        self.contextMenu.addAction(self.removeItemAct)
        self.contextMenu.addSeparator()
        self.contextMenu.addAction(self.addModuleAct)
        self.contextMenu.addAction(self.removeModuleAct)

    def contextMenuEvent(self, event):
        selected = self.selectedItems()
        print("Selected...")
        self.selectedItem = selected[0]
        self.selectedParent = self.selectedItem.parent()

        self.contextMenu.exec(event.globalPos())

    def addLibrary(self):
        return
        if self.selectedParent is None:
            parent = self.selectedItem
        else:
            parent = self.selectedParent
        newItem = QtWidgets.QTreeWidgetItem()
        newItem.setFlags(QtCore.Qt.ItemIsEditable |
                         QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        parent.insertChild(self.cu, newItem)
        self.editItem(newItem)

    def removeLibrary(self):
        if self.selectedParent != None:
            itemText = self.selectedItem.text(0)
            parentText = self.selectedParent.text(0)
            self.useData.libraryDict[parentText][0].remove(itemText)
            self.setItemHidden(self.selectedItem, True)

    def addModule(self):
        return
        if self.selectedParent is None:
            parent = self.selectedItem
        else:
            parent = self.selectedParent
        newItem = QtWidgets.QTreeWidgetItem()
        newItem.setFlags(QtCore.Qt.ItemIsEditable |
                         QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        parent.insertChild(self.cu, newItem)
        self.editItem(newItem)

    def removeModule(self):
        if self.selectedParent != None:
            itemText = self.selectedItem.text(0)
            parentText = self.selectedParent.text(0)
            self.useData.libraryDict[parentText][0].remove(itemText)
            self.setItemHidden(self.selectedItem, True)
