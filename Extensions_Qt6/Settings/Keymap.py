# FIXME QtXml is no longer supported.
from PyQt6 import QtCore, QtGui, QtWidgets, QtXml
from PyQt6.Qsci import QsciScintilla


class GetShortcut(QtWidgets.QDialog):

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent, QtCore.Qt.WindowType.Window | QtCore.Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle(_("New Shortcut"))

        self.accepted = False
        self.keyValue = None

        # Keyword modifiers!
        self.keyword_modifiers = (
            QtCore.Qt.Key.Key_Control, QtCore.Qt.Key.Key_Meta, QtCore.Qt.Key.Key_Shift,
            QtCore.Qt.Key.Key_Alt, QtCore.Qt.Key.Key_Menu)

        mainLayout = QtWidgets.QVBoxLayout(self)

        self.keyLine = QtWidgets.QLineEdit()
        self.keyLine.setReadOnly(True)
        self.keyLine.installEventFilter(self)
        mainLayout.addWidget(self.keyLine)

        hbox = QtWidgets.QHBoxLayout()
        mainLayout.addLayout(hbox)

        okButton = QtWidgets.QPushButton(_("Accept"))
        okButton.clicked.connect(self.saveShortcut)
        hbox.addWidget(okButton)

        cancelButton = QtWidgets.QPushButton(_("Cancel"))
        cancelButton.clicked.connect(self.close)
        hbox.addWidget(cancelButton)

    def saveShortcut(self):
        self.close()
        self.keysequence = QtGui.QKeySequence(self.keyLine.text())
        self.accepted = True

    def setShortcut(self, txt):
        self.keyLine.setText(txt)

    def eventFilter(self, watched, event):
        if event.type() == QtCore.QEvent.Type.KeyPress:
            self.keyPressEvent(event)
            return True
        return False

    def keyPressEvent(self, event):
        # modifier can not be used as shortcut
        if event.key() in self.keyword_modifiers:
            return

        if event.key() == QtCore.Qt.Key.Key_Backtab and event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier:
            self.keyValue = QtCore.Qt.Key.Key_Tab
        else:
            self.keyValue = event.key()
        if event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier:
            self.keyValue += QtCore.Qt.Key.SHIFT
        if event.modifiers() & QtCore.Qt.KeyboardModifier.ControlModifier:
            self.keyValue += QtCore.Qt.Key.CTRL
        if event.modifiers() & QtCore.Qt.KeyboardModifier.AltModifier:
            self.keyValue += QtCore.Qt.Key.ALT
        if event.modifiers() & QtCore.Qt.KeyboardModifier.MetaModifier:
            self.keyValue += QtCore.Qt.Key.META
        # set the keys
        self.setShortcut(QtGui.QKeySequence(self.keyValue).toString())


class Keymap(QtWidgets.QDialog):

    def __init__(self, useData, projectWindowStack, parent):
        QtWidgets.QDialog.__init__(self, parent, QtCore.Qt.WindowType.WindowCloseButtonHint)

        self.setWindowTitle(_('Keymap'))
        self.resize(500, 400)

        self.parent = parent
        self.useData = useData
        self.projectWindowStack = projectWindowStack

        mainLayout = QtWidgets.QVBoxLayout()
        self.setLayout(mainLayout)

        self.shortcutsView = QtWidgets.QTreeWidget()
        self.shortcutsView.setHeaderLabels([_("Function"), _("Shortcut")])
        self.shortcutsView.setColumnWidth(0, 450)
        self.shortcutsView.setSortingEnabled(True)
        self.shortcutsView.sortByColumn(0, QtCore.Qt.SortOrder.AscendingOrder)
        self.shortcutsView.itemDoubleClicked.connect(self.newShortcut)
        mainLayout.addWidget(self.shortcutsView)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setContentsMargins(0, 0, 0, 0)
        mainLayout.addLayout(hbox)

        hbox.addStretch(1)
        load_defaults_button = QtWidgets.QPushButton(self.tr(_("Default")))
        load_defaults_button.clicked.connect(self.setDefaultShortcuts)
        hbox.addWidget(load_defaults_button)

        self.applyButton = QtWidgets.QPushButton(_("Apply"))
        self.applyButton.clicked.connect(self.save)
        hbox.addWidget(self.applyButton)

        self.updateShortcutsView()

    def validateShortcut(self, keysequence):
        """
        Validate a shortcut
        """
        if keysequence.isEmpty():
            return True

        currentItem = self.shortcutsView.currentItem()
        keystr = keysequence.toString()

        for index in range(self.shortcutsView.topLevelItemCount()):
            topLevelItem = self.shortcutsView.topLevelItem(index)

            for i in range(topLevelItem.childCount()):
                item = topLevelItem.child(i)
                if item.text(1) == keystr:
                    if currentItem != item:
                        reply = QtWidgets.QMessageBox.warning(self,
                                                          _('Shortcut'),
                                                          _("Shortcut already in use by '{0}'\n\nReplace it?").format(
                                                              item.text(0)),
                                                          QtWidgets.QMessageBox.StandardButton.Yes, 
                                                          QtWidgets.QMessageBox.StandardButton.No)
                        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                            item.setText(1, "")
                            return True
                        else:
                            return False

        return True

    def newShortcut(self, item, column):
        if item.childCount():
            return
        shortcut = GetShortcut(self)
        shortcut.setShortcut(QtGui.QKeySequence(item.text(1)).toString())
        shortcut.exec()
        if shortcut.accepted:
            if self.validateShortcut(shortcut.keysequence):
                item = self.shortcutsView.currentItem()
                topLevelItem = item.parent()
                item.setText(
                    1, shortcut.keysequence.toString())
                group = topLevelItem.text(0)
                shortName = shortcut.keysequence.toString()
                self.useData.CUSTOM_SHORTCUTS[group][
                    item.text(0)][0] = shortName
                if group == "Editor":
                    if shortcut.keyValue is None:
                        return
                    self.useData.CUSTOM_SHORTCUTS[group][
                        item.text(0)][1] = shortcut.keyValue

    def save(self):
        self.bindKeymap()
        self.saveKeymap()

    def saveKeymap(self, path=None):
        dom_document = QtXml.QDomDocument("keymap")

        keymap = dom_document.createElement("keymap")
        dom_document.appendChild(keymap)

        for key, value in self.useData.CUSTOM_SHORTCUTS.items():
            root = dom_document.createElement(key)
            keymap.appendChild(root)

            for short, func in value.items():
                tag = dom_document.createElement(short)
                if key == "Editor":
                    shortName = func[0]
                    keyValue = str(func[1])
                    tag.setAttribute("shortcut", shortName)
                    tag.setAttribute("value", keyValue)
                else:
                    tag.setAttribute("shortcut", func)
                root.appendChild(tag)

        if path is None:
            path = self.useData.appPathDict["keymap"]
        file = open(path, "w")
        file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        file.write(dom_document.toString())
        file.close()

    def bindKeymap(self):
        for i in range(self.projectWindowStack.count() - 1):
            window = self.projectWindowStack.widget(i)
            window.setKeymap()
            editorTabWidget = window.editorTabWidget
            editorTabWidget.setKeymap()
            for i in range(editorTabWidget.count()):
                editor = editorTabWidget.getEditor(i)
                editor2 = editorTabWidget.getCloneEditor(i)
                editor.setKeymap()
                editor2.setKeymap()

    def updateShortcutsView(self):
        self.shortcutsView.clear()
        keyList = ['Editor', 'Ide']
        for i in keyList:
            mainItem = QtWidgets.QTreeWidgetItem(self.shortcutsView)
            mainItem.setText(0, i)
            if i == "Editor":
                for function, action in self.useData.CUSTOM_SHORTCUTS[i].items():
                    item = QtWidgets.QTreeWidgetItem(
                        mainItem, [function, action[0]])
            else:
                for function, action in self.useData.CUSTOM_SHORTCUTS[i].items():
                    item = QtWidgets.QTreeWidgetItem(mainItem, [function, action])
            mainItem.setExpanded(True)

    def setDefaultShortcuts(self):
        reply = QtWidgets.QMessageBox.warning(self, _("Default Keymap"),
                                          _("Setting keymap to default will wipe away your current keymap.\n\nProceed?"),
                                          QtWidgets.QMessageBox.StandardButton.Yes | 
                                          QtWidgets.QMessageBox.StandardButton.No)
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            for key, value in self.useData.DEFAULT_SHORTCUTS['Ide'].items():
                default = self.useData.DEFAULT_SHORTCUTS['Ide'][key]
                self.useData.CUSTOM_SHORTCUTS['Ide'][key] = default

            sc = QsciScintilla()
            standardCommands = sc.standardCommands()

            for key, value in self.useData.DEFAULT_SHORTCUTS['Editor'].items():
                default = self.useData.DEFAULT_SHORTCUTS['Editor'][key]
                command = standardCommands.find(default[1])
                keyValue = command.key()
                self.useData.CUSTOM_SHORTCUTS[
                    'Editor'][key] = [default[0], keyValue]
            self.save()
            self.useData.loadKeymap()
            self.updateShortcutsView()
        else:
            return
