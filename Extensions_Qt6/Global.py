
import sys
from PyQt6 import QtCore, QtGui, QtWidgets


def getDefaultFont():
    # Platform specific fonts
    if sys.platform == 'win32':
        font = 'Lucida Console'
        font_size = 9
    elif sys.platform == 'darwin':
        font = 'Monaco'
        font_size = 10
    else:
        font = 'Bitstream Vera Sans Mono'
        font_size = 10

    return QtGui.QFont(font, font_size)


def iconFromPath(path):
    fileInfo = QtCore.QFileInfo(path)
    iconProvider = QtWidgets.QFileIconProvider()
    icon = iconProvider.icon(fileInfo)

    return icon
