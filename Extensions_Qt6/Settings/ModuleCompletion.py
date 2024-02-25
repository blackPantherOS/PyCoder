from PyQt6 import QtCore, QtGui, QtWidgets, QtXml

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

        self.addItemAct.setEnabled(False)
        self.addModuleAct.setEnabled(False)
        self.removeItemAct.setEnabled(False)
        self.removeModuleAct.setEnabled(False)

    def contextMenuEvent(self, event):
        selected = self.selectedItems()
        if selected:
            self.selectedItem = selected[0]
            self.selectedParent = self.selectedItem.parent()
            self.addItemAct.setEnabled(True)
            self.addModuleAct.setEnabled(True)
            self.removeItemAct.setEnabled(True)
            self.removeModuleAct.setEnabled(True)
        else:
            #self.addItemAct.setEnabled(True)
            self.addModuleAct.setEnabled(True)

        self.contextMenu.exec(event.globalPos())

    def addLibrary(self):
        if hasattr(self, 'selectedParent'):
            if self.selectedParent is None:
                parent = self.selectedItem
            else:
                parent = self.selectedParent
            newItem = QtWidgets.QTreeWidgetItem()
            newItem.setFlags(newItem.flags() |
                             QtCore.Qt.ItemFlag.ItemIsEditable |
                             QtCore.Qt.ItemFlag.ItemIsSelectable | 
                             QtCore.Qt.ItemFlag.ItemIsEnabled)
            parent.insertChild(0, newItem)
            self.editItem(newItem)
            QtWidgets.QTreeWidgetItem.setHidden(parent, False)

        else:
            print("Unfinished function!")

    def addModule(self):
        if hasattr(self, 'selectedParent'):
            if self.selectedParent is None:
                parent = self.selectedItem
            else:
                parent = self.selectedParent
        else:
            parent = None

        newItem = QtWidgets.QTreeWidgetItem()
        newItem.setFlags(newItem.flags() |
                         QtCore.Qt.ItemFlag.ItemIsEditable |
                         QtCore.Qt.ItemFlag.ItemIsSelectable | 
                         QtCore.Qt.ItemFlag.ItemIsEnabled)
        if parent is not None:
            parent.insertChild(0, newItem)
        else:
            parentText = "RenameIt"
            newItem.setText(0, parentText) 
            newItem.setCheckState(0, QtCore.Qt.CheckState.Checked)
            self.addTopLevelItem(newItem)
            #self.selectedItem = newItem
            #parent = self.selectedItem

        self.editItem(newItem)
        #QtWidgets.QTreeWidgetItem.setHidden(parent, False)
        print("Unfinished function!")

    def removeLibrary(self):
        if hasattr(self, 'selectedItem') and self.selectedItem is not None:
            if self.selectedParent is not None:
                itemText = self.selectedItem.text(0)
                parentText = self.selectedParent.text(0)
                self.useData.libraryDict[parentText][0].remove(itemText)
                QtWidgets.QTreeWidgetItem.setHidden(self.selectedItem, True)

    def removeModule(self):
        if hasattr(self, 'selectedParent') and self.selectedParent is not None:
            itemText = self.selectedItem.text(0)
            parentText = self.selectedParent.text(0)
            self.useData.libraryDict[parentText][0].remove(itemText)
            QtWidgets.QTreeWidgetItem.setHidden(self.selectedItem, True)

