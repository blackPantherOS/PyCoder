import sys
import difflib

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.Qsci import QsciScintillaBase, QsciLexerCustom

from Extensions_Qt6.BaseScintilla import BaseScintilla
from Extensions_Qt6 import Global


class FormatLexer(QsciLexerCustom):

    def __init__(self, parent=None):
        QsciLexerCustom.__init__(self, parent)

        self._styles = {
            0: 'Default',
            1: 'NewText',
            2: 'DeletedText',
            3: 'ReplacedText',
            4: 'LineNumber'
            }
        for key in self._styles:
            setattr(self, self._styles[key], key)

    def description(self, style):
        return self._styles.get(style, '')

    def defaultColor(self, style):
        return QtGui.QColor('#000000')

    def defaultPaper(self, style):
        if style == self.Default:
            return QtGui.QColor('#ffffff')
        elif style == self.NewText:
            return QtGui.QColor('#DDFFDD')
        elif style == self.DeletedText:
            return QtGui.QColor('#FFDDDD')
        elif style == self.ReplacedText:
            return QtGui.QColor('#BED6ED')
        elif style == self.LineNumber:
            return QtGui.QColor('#EAF2F5')
        return QtGui.QColor('#ffffff')

    def defaultFont(self, style):
        if style == self.Default:
            return Global.getDefaultFont()
        elif style == self.NewText:
            return Global.getDefaultFont()
        elif style == self.DeletedText:
            return Global.getDefaultFont()
        elif style == self.ReplacedText:
            return Global.getDefaultFont()
        elif style == self.LineNumber:
            return Global.getDefaultFont()
        return QsciLexerCustom.defaultFont(self, style)

    def defaultEolFill(self, style):
        return True

    def styleText(self, start, end):
        editor = self.editor()
        if editor is None:
            return

        # scintilla works with encoded bytes, not decoded characters.
        # this matters if the source contains non-ascii characters and
        # a multi-byte encoding is used (e.g. utf-8)
        source = ''
        if end > editor.length():
            end = editor.length()
        if end > start:
            if sys.hexversion >= 0x02060000:
                # faster when styling big files, but needs python 2.6
                source = bytearray(end - start)
                editor.SendScintilla(
                    editor.SCI_GETTEXTRANGE, start, end, source)
            else:
                source = editor.text().encode('utf-8')
        if not source:
            return

        self.startStyling(start, 0x1f)


class DiffWindow(BaseScintilla):

    def __init__(self, editor=None, snapShot=None, parent=None):
        QtWidgets.QTextEdit.__init__(self, parent)

        self.setReadOnly(True)
        self.setMarginWidth(1, 0)
        self.lexer = FormatLexer(self)
        self.setLexer(self.lexer)
        self.setObjectName("editor")

        self.editor = editor
        self.snapShot = snapShot

        self.setStyleSheet("QsciScintilla {border: none;}")

    def generateUnifiedDiff(self, a=None, b=None):
        self.clear()

        if a is None:
            a = self.snapShot.text().splitlines()
        if b is None:
            b = self.editor.text().splitlines()

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        lines = 0
        for line in difflib.unified_diff(a, b, _("Deleted"), _("Added")):
            if line.startswith('+') or line.startswith('>'):
                styleType = 1
            elif line.startswith('-') or line.startswith('<'):
                styleType = 2
            elif line.startswith('@@'):
                styleType = 4
            else:
                styleType = 0
            self.appendText(line, styleType)
            lines += 1

        if lines == 0:
            self.appendText(_('Nothing has changed.'), 0)

        QtWidgets.QApplication.restoreOverrideCursor()

        return (lines != 0)

    def generateContextDiff(self):
        self.clear()

        a = self.snapShot.text().splitlines()
        b = self.editor.text().splitlines()

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        lines = 0
        for line in difflib.context_diff(a, b, _("Original"), _("Current")):
            if line.startswith('+'):
                styleType = 1
            elif line.startswith('-'):
                styleType = 2
            elif line.startswith('!'):
                styleType = 3
            elif line.startswith('*** '):
                styleType = 4
            else:
                styleType = 0
            self.appendText(line, styleType)
            lines += 1

        if lines == 0:
            self.appendText(_('Nothing has changed.'), 0)

        QtWidgets.QApplication.restoreOverrideCursor()

    def appendText(self, text, styleType):
        start = self.length()
        self.SendScintilla(QsciScintillaBase.SCI_STARTSTYLING, start)
        self.append(text + "\n")
        self.recolor(start, -1)
        self.SendScintilla(QsciScintillaBase.SCI_SETSTYLING, len(text),
                           styleType)
