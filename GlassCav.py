# ----------------------------------
# author : FreeHe
# github : https://github.com/FreeHe
# ----------------------------------
import time
import sys
import re
import os

from GlassWin import GlassWin

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QSplashScreen, QProgressBar, QWidget, QApplication, QMainWindow, QDesktopWidget, QLabel, \
    QHBoxLayout, QVBoxLayout

DIR = os.getcwd()
DIR = DIR.replace('\\', '/')
os.chdir(DIR)


class GlassSplashScreen(QSplashScreen):
    def __init__(self, app, *args, **kwargs):
        super(GlassSplashScreen, self).__init__(*args, **kwargs)
        screen = QDesktopWidget().availableGeometry().center()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.stop_process = None
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.AlignHCenter)
        self.setEnabled(False)
        self.layout = QVBoxLayout()
        self.FreeHe_GlassCav = QLabel('FreeHe-GlassCav')
        self.FreeHe_GlassCav.setStyleSheet('QLabel{font-size:50px;color:#cf0;text-align:center}')
        self.FreeHe_GlassCav.setFont(QFont("Ink Free"))
        self.setFixedSize(500, 130)
        self.progressBar = QProgressBar()
        self.progressBar.setMaximum(10)
        self.progressBar.setFixedSize(500, 20)
        self.setFixedSize(500, 150)
        self.setStyleSheet('''
            QProgressBar {
                text-align: center;
                background-color: #202020;
                border-color: #202020;
                color: blue;
                font-size: 20px;
            }
            QProgressBar::chunk {
                background-color: #cf0;
            }
            GlassSplashScreen {
                background-color: #202020;
            }
        ''')
        qr = self.frameGeometry()
        qr.moveCenter(screen)
        self.layout.addWidget(self.FreeHe_GlassCav)
        self.layout.addWidget(self.progressBar)
        self.setLayout(self.layout)
        self.move(qr.topLeft())

    def show_(self):
        self.show()
        for i in range(1, 10):
            self.progressBar.setValue(i)
            t = time.time()
            while time.time() < t + 0.1:
                ...
            app.processEvents()
            if self.stop_process:
                break

    def finish_(self, w):
        self.stop_process = True
        self.finish(w)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gss = GlassSplashScreen(app)
    gss.show_()
    win = GlassWin(DIR)
    win.show()
    gss.finish_(win)
    sys.exit(app.exec_())
