from PyQt5 import QtCore, QtGui, QtWidgets


class Notification(QtWidgets.QLabel):

    def __init__(self, parent=None):
        QtWidgets.QLabel.__init__(self, parent)

        self.setMinimumHeight(25)
        self.setMargin(5)
        
        self.easingCurve = QtCore.QEasingCurve.OutCubic

        # crash fix by vector
        try:
            self.showAnimation = QtCore.QPropertyAnimation(self, 'maximumWidth')
            print("Animation:", self.showAnimation)
            self.showAnimation.setDuration(200)
            self.showAnimation.setEasingCurve(self.easingCurve)
        except:
            pass

        self.setStyleSheet("""background: #1A1A1A;
                                color: white;
                                border: 1px solid #72A4CE;
                                border-radius: 0px;
                                border-left: 5px solid #72A4CE;
                            """)

    def mousePressEvent(self, event):
        self.hide()

    def showMessage(self, mess):
        self.hide()
        self.setText(mess)
        self.adjustSize()
        
        max_width = self.geometry().width()
        self.showAnimation.setEndValue(max_width + 10)
        self.setMaximumWidth(0)
        self.show()
        self.showAnimation.start()
        
        
