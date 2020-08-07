# ----------------------------------
# author : FreeHe
# github : https://github.com/FreeHe
# ----------------------------------
import os

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QTimer
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QHBoxLayout, QLineEdit, QLabel, QDesktopWidget, QSlider, QCheckBox, QFileDialog

from GlassUtils import write_pickle


class ButLabel(QLabel):
    signal = pyqtSignal()

    def __init__(self, *args):
        super(ButLabel, self).__init__(*args)

    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent) -> None:
        self.signal.emit()


class GlassFile(QLabel):
    def __init__(self, dir_, DIR):
        super(GlassFile, self).__init__()
        self.setFixedSize(650, 80)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAlignment(Qt.AlignCenter)
        self.layout = QHBoxLayout()
        self.dir = DIR
        self.input = QLineEdit()
        self.input.setFont(QFont('Ink Free'))
        self.input.setFixedSize(500, 50)
        self.input.setText(dir_)
        self.browser = ButLabel()
        self.browser.setPixmap(QPixmap(DIR + '/icon/browser.png'))
        self.browser.signal.connect(self.select_dir)

        self.check = ButLabel()
        self.check.signal.connect(self.check_dir)
        self.check.setPixmap(QPixmap(DIR + '/icon/check.png'))
        self.layout.addWidget(self.input)
        self.layout.addWidget(self.browser)
        self.layout.addWidget(self.check)
        self.setLayout(self.layout)
        self.setStyleSheet('''
            GlassFile {
                background-color: #202020;
                padding: 0;
            }
            QLineEdit {
                background-color: #202020;
                color: #505050;
                font-size: 30px;
                border-width: 1px;
                border-style: solid;
                border-color: #505050;
                border-radius: 10px;
            }
        ''')

    def select_dir(self):
        dir_ = QFileDialog.getExistingDirectory(self, '选择输出路径', './')
        if os.path.isdir(dir_):
            self.input.setText(dir_)
            write_pickle(dir_, self.dir)

    def check_dir(self):
        self.hide()


class GlassCam(QLabel):
    def __init__(self):
        super(GlassCam, self).__init__()
        self.m_drag = None
        self.m_DragPosition = None
        self.setFixedSize(300, 300)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.screen = QDesktopWidget()
        self.setStyleSheet('''
            GlassCam {
                background-color: #202020;
            }
        ''')

    def show_(self):
        self.show()

    def hide_(self):
        self.hide()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.m_drag = True
            self.m_DragPosition = e.globalPos() - self.pos()
            e.accept()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.m_drag = False
            current = e.globalPos() - self.m_DragPosition
            position = current + QPoint(150, 150)
            x = 0 if position.x() < int(self.screen.width() / 2) else self.screen.width() - 300
            y = 0 if position.y() < int(self.screen.height() / 2) else self.screen.height() - 300
            self.move(QPoint(x, y))

    def mouseMoveEvent(self, e):
        if Qt.LeftButton and self.m_drag:
            self.move(e.globalPos() - self.m_DragPosition)
            e.accept()


class GlassV(QLabel):
    def __init__(self, DIR, parant):
        super(GlassV, self).__init__()
        self.setToolTip('设置视频比特率,数值越大越清晰,占用系统资源越多')
        self.setFont(QFont('Ink Free'))
        self.setFixedSize(750, 80)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.layout = QHBoxLayout()
        self.bit_rate = QLabel('1500k')
        self.bit_rate.setFixedSize(150, 50)
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(1000)
        self.slider.setMaximum(8000)
        self.slider.setSingleStep(500)
        self.slider.setValue(1500)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(500)
        self.slider.valueChanged.connect(lambda: self.bit_rate.setText(str(self.slider.value()) + 'k'))
        self.slider.setFixedSize(500, 50)
        self.check = ButLabel()
        self.check.setPixmap(QPixmap(DIR + '/icon/check.png'))
        self.check.signal.connect(lambda: self.hide())
        self.check.signal.connect(parant.restart)
        self.layout.addWidget(self.slider)
        self.layout.addWidget(self.bit_rate)
        self.layout.addWidget(self.check)
        self.setLayout(self.layout)
        self.setStyleSheet('''
            GlassV {
                background-color: #202020;
            }
            QLabel {
                font-size: 30px;
                color: #505050;
            }
            QToolTip {
                background-color: #202020;
                padding: 20px;
                font-size: 30px;
                border-radius: 40px
            }
                QSlider::handle:horizontal{
                width:24px;
                background-color:rgb(204,255,0);
                margin:-11px 0px -11px 0px;
                border-radius:12px;
            }
            QSlider::groove:horizontal{
                height:2px;
                background-color:rgb(219,219,219);
            }
            QSlider::add-page:horizontal{
                background-color:rgb(219,219,219);
            }
            QSlider::sub-page:horizontal{
                background-color:rgb(26,217,110);
            }
        ''')


class GlassA(QLabel):
    def __init__(self, DIR, parant):
        super(GlassA, self).__init__()
        self.setFixedSize(750, 80)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFont(QFont('Ink Free'))
        self.cb1 = QCheckBox('Realtak(R) Audio')
        self.cb1.setFixedSize(350, 50)
        self.cb1.setChecked(True)
        self.cb2 = QCheckBox('mike')
        self.cb2.setFixedSize(350, 50)
        self.cb2.setChecked(False)
        self.check = ButLabel()
        self.check.setPixmap(QPixmap(DIR + '/icon/check.png'))
        self.check.signal.connect(self.check_a)
        self.check.signal.connect(parant.restart)
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.cb1)
        self.layout.addWidget(self.cb2)
        self.layout.addWidget(self.check)
        self.setStyleSheet('''
            GlassA {
                background-color: #202020;
                font-size: 25px;
                color: #505050;
            }
            QCheckBox {
                color: #505050;
                font-size: 30px;
                margin-right: 20px;
            }
            QCheckBox::indicator {
                Width:50px;
                Height:50px;
                border-radius: 25px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #505050;
            }
            QCheckBox::indicator:checked {
                background-color: #cf0;
            }
                
        ''')
        self.setLayout(self.layout)

    def check_a(self):
        self.hide()


class GlassAction(QLabel):
    def __init__(self, status, DIR):
        super(GlassAction, self).__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setFixedSize(200, 200)
        screen = QDesktopWidget().availableGeometry().center()
        qr = self.frameGeometry()
        qr.moveCenter(screen)
        self.move(qr.topLeft())
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.hide)
        if status == 'pause':
            self.setPixmap(QPixmap(DIR + '/icon/暂停.png'))
        elif status == 'stop':
            self.setPixmap(QPixmap(DIR + '/icon/结束.png'))
        else:
            self.setPixmap(QPixmap(DIR + '/icon/开始.png'))

    def show_(self):
        self.show()
        self.timer.start(400)
