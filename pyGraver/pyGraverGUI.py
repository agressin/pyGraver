from PyQt5 import uic
import os.path as op
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
from PyQt5.QtGui import QImage, QPixmap, QFont, QFontMetricsF, QPainter
from PyQt5.QtCore import Qt, QTimer
import sys
from pyGraver import pyGraver
import serial.tools.list_ports

# TODO :
# - set burning time / power garver.setPWD()


# #######################################################################
# pyGraverGUI
class pyGraverGUI(QDialog):
    # #######################################################################
    # init
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi(op.join(op.dirname(__file__), "pyGraverGUI.ui"), self)
        #
        self.imgToBurn = QImage()
        self.graver = None
        self.previewMode = False
        self.pbUp.clicked.connect(self.onClickUp)
        self.pbDown.clicked.connect(self.onClickDown)
        self.pbLeft.clicked.connect(self.onClickLeft)
        self.pbRight.clicked.connect(self.onClickRight)
        self.pbBurn.clicked.connect(self.onClickBurn)
        self.pbGo.clicked.connect(self.onClickGo)
        self.pbStop.clicked.connect(self.onClickStop)
        self.pbPause.clicked.connect(self.onClickPause)
        self.pbConnect.clicked.connect(self.onClickConnect)
        self.pbRefresh.clicked.connect(self.onClickRefresh)
        self.pbPreview.clicked.connect(self.onClickPreview)
        self.pbLoad.clicked.connect(self.onClickLoad)
        self.pbGenerate.clicked.connect(self.onClickGenerate)

        self.onClickRefresh()

    def onClickUp(self):
        if self.graver is None:
            print("please connect before")
            return
        self.graver.moveUp()

    def onClickDown(self):
        print("onClickDown")
        if self.graver is None:
            print("please connect before")
            return
        self.graver.moveDown()

    def onClickLeft(self):
        if self.graver is None:
            print("please connect before")
            return
        self.graver.moveLeft()

    def onClickRight(self):
        if self.graver is None:
            print("please connect before")
            return
        self.graver.moveRight()

    def onClickLoad(self):
        print("onClickLoad")
        self.imgToBurn = QImage(self.leFileName.text())
        self.laImg.setPixmap(QPixmap.fromImage(self.imgToBurn))

    def onClickGenerate(self):
        doc = self.teText.document()
        font = QFont()
        font.setPointSizeF(self.sbFontSize.value())
        doc.setDefaultFont(font)
        m = QFontMetricsF(font)

        nbLines = doc.lineCount()
        width = max([m.width(ll) for ll in doc.toPlainText().split("\n")])
        pixmap = QPixmap(width*1.2, m.lineSpacing()*nbLines*1.2)

        pixmap.fill(Qt.white)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing, True)
        doc.drawContents(painter)
        painter.end()

        self.laImg.setPixmap(pixmap)
        self.imgToBurn = QImage(pixmap.toImage())

    def onClickPreview(self):
        if self.graver is None:
            print("please connect before")
            return

        if self.previewMode:
            self.graver.stopShowWindow()
            self.previewMode = False
        else:
            x, y = self.sbPosX.value(), self.sbPosY.value()
            w = self.imgToBurn.width()
            h = self.imgToBurn.height()
            self.graver.showWindow(x, y, w, h)
            self.previewMode = True

    def onClickBurn(self):
        if self.graver is None:
            print("please connect before")
            return
        if self.previewMode:
            self.onClickPreview()
        x, y = self.sbPosX.value(), self.sbPosY.value()
        self.graver.sendImage(self.imgToBurn, x, y)
        self.refreshProgressBar()

    def onClickGo(self):
        if self.graver is None:
            print("please connect before")
            return
        if self.previewMode:
            self.onClickPreview()
        self.graver.moveXY(self.sbPosX.value(), self.sbPosY.value())

    def onClickStop(self):
        if self.graver is None:
            print("please connect before")
            return
        self.graver.stopCarving()
        self.graver.close()

    def onClickPause(self):
        if self.graver is None:
            print("please connect before")
            return
        self.graver.pauseCarving()

    def onClickConnect(self):
        port = self.cbListPort.currentText()
        if self.graver is not None:
            self.graver.close()
            self.graver = None
        self.graver = pyGraver(port)

    def onClickRefresh(self):
        self.cbListPort.clear()
        for port in serial.tools.list_ports.comports():
            print(port)
            self.cbListPort.addItem(port.device)

    def refreshProgressBar(self):
        if self.graver is not None:
            percent = self.graver.carvingPercentProgress
            self.pbProgressBurn.setValue(percent)
            if percent < 100:
                QTimer.singleShot(200, self.refreshProgressBar)
            else:
                self.graver.carvingPercentProgress = 0


if __name__ == '__main__':

    app = QApplication(sys.argv)

    main_window = QMainWindow()
    main_widget = pyGraverGUI(None)
    main_window.setCentralWidget(main_widget)
    main_window.show()
    sys.exit(app.exec_())
