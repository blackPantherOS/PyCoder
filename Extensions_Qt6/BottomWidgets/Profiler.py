import os
import locale
import pstats
from PyQt6 import QtCore, QtGui, QtWidgets


class Profiler(QtWidgets.QTreeWidget):

    def __init__(self, useData, bottomStackSwitcher, parent=None):
        QtWidgets.QTreeWidget.__init__(self, parent)

        self.useData = useData
        self.bottomStackSwitcher = bottomStackSwitcher

        self.setHeaderLabels(["ncalls", "tottime", "percall",
                              "cumtime", "filename", "# line", "function"])
        self.setSortingEnabled(True)
        self.sortByColumn(4, QtCore.Qt.SortOrder.AscendingOrder)

    def changeView(self, index):
        self.viewStack.setCurrentIndex(index)

    def processStarted(self):
        self.errorLabel.clear()
        self.errooIconLabel.hide()
        self.errorLabel.hide()
        self.profileButton.setDisabled(True)

    def writeProcessError(self):
        default_encoding = locale.getpreferredencoding()
        text = \
            self.process.readAllStandardError().data().decode(default_encoding)
        self.errorLabel.setText(text)
        self.errooIconLabel.show()
        self.errorLabel.show()

    def viewProfile(self, file=None):
        if file is None:
            file = os.path.join("temp", "profile")
        self.p = pstats.Stats(file)
        self.p.calc_callees()
        self.stats = self.p.stats
        # self.saveButton.setDisabled(False)

        self.clear()

        for func, (cc, nc, tt, ct, callers) in self.stats.items():
            item = QtWidgets.QTreeWidgetItem()
            item.setText(0, str(cc))
            item.setText(1, str(nc))
            item.setText(2, str(tt))
            item.setText(3, str(ct))

            item.setText(4, str(func[0]))
            item.setText(5, str(func[1]))
            item.setText(6, str(func[2]))

            child = QtWidgets.QTreeWidgetItem()
            for caller, (cc1, nc1, tt1, ct1) in callers.items():
                child.setIcon(
                    0, QtGui.QIcon(os.path.join("Resources", "images", "lightning")))
                child.setText(0, str(cc))
                child.setText(1, str(nc1))
                child.setText(2, str(tt1))
                child.setText(3, str(ct1))

                child.setText(4, caller[0])
                child.setText(5, str(caller[1]))
                child.setText(6, caller[2])
            for i in range(7):
                child.setForeground(i, QtGui.QBrush(QtGui.QColor("#FF0000")))
            item.addChild(child)
            self.addTopLevelItem(item)
        self.bottomStackSwitcher.setCurrentWidget(self)

    def saveProfile(self):
        options = QtWidgets.QFileDialog.Options()
        savepath = os.path.join(self.useData.getLastOpenedDir(),
                                self.projectWindowStack.currentWidget().projectPathDict["name"] + '_' + QtCore.QDateTime().currentDateTime().toString().replace(' ', '_').replace(':', '-'))
        savepath = os.path.normpath(savepath)
        fileName = QtWidgets.QFileDialog.getSaveFileName(self,
                                                     "Save profile", savepath,
                                                     "Profiles (*.cProfile)", options)[0]
        if fileName:
            try:
                self.useData.saveLastOpenedDir(os.path.split(fileName)[0])
                self.p.dump_stats(fileName)
            except Exception as err:
                message = QtWidgets.QMessageBox.warning(
                    self, "Save Profile", str(err))

    def openProfile(self):
        options = QtWidgets.QFileDialog.Options()
        fileName = QtWidgets.QFileDialog.getOpenFileName(self,
                                                     "Open profile", self.useData.getLastOpenedDir(
                                                     ),
                                                     "Profiles (*.cProfile)", options)[0]
        if fileName:
            try:
                self.useData.saveLastOpenedDir(os.path.split(fileName)[0])
                self.viewProfile(fileName)
            except Exception as err:
                message = QtWidgets.QMessageBox.warning(
                    self, "Open Profile", str(err))
