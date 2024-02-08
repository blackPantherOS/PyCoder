from PyQt6 import QtCore, QtGui, QtWidgets


class StackSwitcher(QtWidgets.QWidget):

    changed = QtCore.pyqtSignal(str)

    def __init__(self, stack, parent=None):
        QtWidgets.QDialog.__init__(self, parent)

        self.stack = stack
        self.lastIndex = 0

        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainLayout.setSpacing(0)
        self.setLayout(self.mainLayout)

        self.buttonGroup = QtWidgets.QButtonGroup()
        self.buttonGroup.setExclusive(True)
        self.buttonGroup.buttonPressed.connect(self.setIndex)

    def addButton(self, name=None, icon=None, toolTip=None):
        button = QtWidgets.QPushButton()
        if name is not None:
            button.setText(name)
        if toolTip is not None:
            button.setToolTip(toolTip)
        button.setCheckable(True)
        if icon is not None:
            button.setIcon(icon)
        self.buttonGroup.addButton(button)
        self.buttonGroup.setId(button, self.lastIndex)
        self.mainLayout.addWidget(button)

        self.lastIndex += 1

    def setIndex(self, button):
        index = self.buttonGroup.id(button)
        self.stack.setCurrentIndex(index)
        self.changed.emit(button.text())

    def setCount(self, widget, text):
        index = self.stack.indexOf(widget)
        self.buttonGroup.button(index).setText(text)

    def setCurrentWidget(self, widget):
        index = self.stack.indexOf(widget)
        button = self.buttonGroup.button(index)
        button.setChecked(True)
        self.stack.setCurrentWidget(widget)

        self.changed.emit(button.text())

    def setDefault(self):
        """
        Shows the active button after initialization
        """
        button = self.buttonGroup.button(0)
        button.setChecked(True)
        self.changed.emit(button.text())
