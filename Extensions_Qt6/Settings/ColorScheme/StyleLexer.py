import os
# FIXME QtXml is no longer supported.
from PyQt6 import QtCore, QtGui, QtWidgets, QtXml

from Extensions_Qt6.Settings.ColorScheme.Lexers import PythonLexer
from Extensions_Qt6.Settings.ColorScheme.Lexers import CssLexer
from Extensions_Qt6.Settings.ColorScheme.Lexers import HtmlLexer
from Extensions_Qt6.Settings.ColorScheme.Lexers import XmlLexer
from Extensions_Qt6.Settings.ColorScheme.ColorChooser import ColorChooser


class StyleLexer(QtWidgets.QWidget):

    reloadStyles = QtCore.pyqtSignal()

    def __init__(self, styleProperties, useData, parent=None):
        super(StyleLexer, self).__init__(parent)

        self.styleProperties = styleProperties
        self.useData = useData

        self.setCurrentStyle("Default", "Python")

        mainLayout = QtWidgets.QHBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)

        # style properties
        self.propertyListWidget = QtWidgets.QListWidget()
        self.propertyListWidget.setSortingEnabled(True)
        self.propertyListWidget.currentRowChanged.connect(
            self.newPropertySelected)
        mainLayout.addWidget(self.propertyListWidget)

        self.setLayout(mainLayout)

        # settings
        vbox = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(vbox)

        self.fontColorScopeBG = QtWidgets.QButtonGroup()

        hbox = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel("Foreground")
        label.setStyleSheet("background: lightgrey; padding: 2px;")
        hbox.addWidget(label)
        vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        fontColorScopeAll = QtWidgets.QRadioButton("All")
        self.fontColorScopeBG.addButton(fontColorScopeAll)
        hbox.addWidget(fontColorScopeAll)

        fontColorScopeCurrent = QtWidgets.QRadioButton("Selected")
        self.fontColorScopeBG.addButton(fontColorScopeCurrent)
        fontColorScopeCurrent.setChecked(True)
        hbox.addWidget(fontColorScopeCurrent)

        self.fontColorChooser = ColorChooser()
        self.fontColorChooser.colorChanged.connect(self.updateColor)
        hbox.addWidget(self.fontColorChooser)

        self.backgroundColorScopeBG = QtWidgets.QButtonGroup()

        hbox = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel("Background")
        label.setStyleSheet("background: lightgrey; padding: 2px;")
        hbox.addWidget(label)
        vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        backgroundColorScopeAll = QtWidgets.QRadioButton("All")
        self.backgroundColorScopeBG.addButton(backgroundColorScopeAll)
        hbox.addWidget(backgroundColorScopeAll)

        backgroundColorScopeCurrent = QtWidgets.QRadioButton("Selected")
        self.backgroundColorScopeBG.addButton(backgroundColorScopeCurrent)
        backgroundColorScopeCurrent.setChecked(True)
        hbox.addWidget(backgroundColorScopeCurrent)

        self.backgroundColorChooser = ColorChooser()
        self.backgroundColorChooser.colorChanged.connect(self.updatePaper)
        hbox.addWidget(self.backgroundColorChooser)

        self.fontScopeBG = QtWidgets.QButtonGroup()

        hbox = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel("Font")
        label.setStyleSheet("background: lightgrey; padding: 2px;")
        hbox.addWidget(label)
        vbox.addLayout(hbox)

        hbox = QtWidgets.QHBoxLayout()
        vbox.addLayout(hbox)
        fontScopeAll = QtWidgets.QRadioButton("All")
        self.fontScopeBG.addButton(fontScopeAll)
        hbox.addWidget(fontScopeAll)

        fontScopeCurrent = QtWidgets.QRadioButton("Selected")
        self.fontScopeBG.addButton(fontScopeCurrent)
        fontScopeCurrent.setChecked(True)
        hbox.addWidget(fontScopeCurrent)

        hbox.addStretch(1)

        self.fontButton = QtWidgets.QPushButton("Font")
        self.fontButton.clicked.connect(self.fontChanged)
        hbox.addWidget(self.fontButton)

        vbox.addStretch(1)

    def updatePropertyListWidget(self, groupName):
        if groupName == "Python":
            styles = PythonLexer.styleDescriptions()
        elif groupName == "Css":
            styles = CssLexer.styleDescriptions()
        elif groupName == "Xml":
            styles = XmlLexer.styleDescriptions()
        elif groupName == "Html":
            styles = HtmlLexer.styleDescriptions()

        self.propertyListWidget.clear()
        for i in styles:
            self.propertyListWidget.addItem(i)
        self.propertyListWidget.setCurrentRow(0)

    def createLexer(self, paper, style_name, groupName):
        style = self.loadStyle(style_name, groupName)
        if groupName == "Python":
            lexer = PythonLexer.PythonLexer(style, paper)
        elif groupName == "Xml":
            lexer = XmlLexer.XmlLexer(style, paper)
        elif groupName == "Html":
            lexer = HtmlLexer.HtmlLexer(style, paper)
        elif groupName == "Css":
            lexer = CssLexer.CssLexer(style, paper)
        return lexer

    def setCurrentStyle(self, styleName, groupName):
        self.currentStyle = self.loadStyle(styleName, groupName)

    def loadStyle(self, styleName, groupName):
        if styleName == "Default":
            if groupName == "Python":
                return PythonLexer.defaultStyle()
            elif groupName == "Css":
                return CssLexer.defaultStyle()
            elif groupName == "Xml":
                return XmlLexer.defaultStyle()
            elif groupName == "Html":
                return HtmlLexer.defaultStyle()
        else:
            pass

        style = {}

        stylePath = os.path.join(self.useData.appPathDict["stylesdir"],
                                 groupName, styleName + ".xml")
        # FIXME QtXml is no longer supported.
        dom_document = QtXml.QDomDocument()
        file = open(stylePath, "r")
        x = dom_document.setContent(file.read())
        file.close()

        rootElement = dom_document.documentElement()
        lexerElement = rootElement.firstChild().toElement()
        node = lexerElement.firstChild()

        while node.isNull() is False:
            tag = node.toElement()

            name = tag.text()
            font = tag.attribute("font")
            color = tag.attribute("color")
            size = int(tag.attribute("size"))
            bold = (tag.attribute("bold") == "True")
            italic = (tag.attribute("italic") == "True")
            paper = tag.attribute("paper")

            style[name] = [font, color, size, bold, italic, paper]

            node = node.nextSibling()
        return style

    def updateFontSizeBox(self, widget):
        for i in self.fontSizeList:
            widget.addItem(str(i))

    def newPropertySelected(self):
        currentItem = self.propertyListWidget.currentItem()
        if currentItem is None:
            return
        self.currentPropertyName = currentItem.text()
        self.currentPropertyAttrib = \
            self.currentStyle[self.currentPropertyName]

        color = QtGui.QColor(self.currentPropertyAttrib[1])
        self.fontColorChooser.setColor(self.currentPropertyAttrib[1])

        color = QtGui.QColor(self.currentPropertyAttrib[5])
        self.backgroundColorChooser.setColor(self.currentPropertyAttrib[5])

    def fontChanged(self):

        currentfont = QtGui.QFont(self.currentPropertyAttrib[0], self.currentPropertyAttrib[2])
        font, accepted = QtWidgets.QFontDialog().getFont(currentfont, self)

        if accepted:
            name = font.family()
            size = font.pointSize()
            bold = font.bold()
            italic = font.italic()
            if self.fontScopeBG.checkedButton().text() == 'All':
                for key, value in self.currentStyle.items():
                    value[0] = name
                    value[2] = size
                    value[3] = bold
                    value[4] = italic
                    self.currentStyle[key] = value
            else:
                self.currentPropertyAttrib[0] = name
                self.currentPropertyAttrib[2] = size
                self.currentPropertyAttrib[3] = bold
                self.currentPropertyAttrib[4] = italic
                self.currentStyle[self.currentPropertyName] = \
                    self.currentPropertyAttrib

    def updateColor(self, color):
        self.currentPropertyAttrib[1] = color
        if self.fontColorScopeBG.checkedButton().text() == 'All':
            for key, value in self.currentStyle.items():
                value[1] = color
                self.currentStyle[key] = value
        else:
            self.currentStyle[
                self.currentPropertyName] = self.currentPropertyAttrib
        self.newPropertySelected()

    def updatePaper(self, color):
        self.currentPropertyAttrib[5] = color
        if self.backgroundColorScopeBG.checkedButton().text() == 'All':
            for key, value in self.currentStyle.items():
                value[5] = color
                self.currentStyle[key] = value
        else:
            self.currentStyle[self.currentPropertyName] = \
                self.currentPropertyAttrib
        self.newPropertySelected()
