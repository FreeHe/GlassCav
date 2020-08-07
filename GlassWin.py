# ----------------------------------
# author : FreeHe
# github : https://github.com/FreeHe
# ----------------------------------
import os
import re
import sys
import time
import subprocess as sp

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QPoint, pyqtSignal, QUrl
from PyQt5.QtGui import QPainter, QPixmap, QPainterPath, QFont, QIcon, QDesktopServices
from PyQt5.QtWidgets import QFrame, QDesktopWidget, QHBoxLayout, QLabel, QToolTip, QFileDialog

from GlassEffects import GlassFile, GlassCam, GlassV, GlassA, GlassAction
from GlassUtils import read_pickle


def conf(DIR, bitrate='1500k', enable_a1=True, enable_a2=True, dir_='./'):
    mp = re.compile('麦克风[^0]*\)')
    DIR = DIR.replace('/', '\\\\')
    exe = DIR + "\dll\\ffmpeg.exe -f dshow -i video='screen-capture-recorder' -f dshow -i {}{} -c:a aac -c:v h264_qsv -b:v {} {}"
    e_a1 = "audio='virtual-audio-capturer'"
    powershell = sp.Popen('where powershell', shell=True, stdout=sp.PIPE)
    powershell = powershell.stdout.read(2048).decode('GBK').strip()
    powershell = powershell.replace('\\', '//')
    microphone = sp.Popen(r'.\dll\\ffmpeg.exe -f dshow -list_devices true -i dummy', shell=True, stderr=sp.PIPE)
    microphone = microphone.stderr.read(2048).decode('utf8')
    microphone = mp.search(microphone).group()
    e_a2 = " -f dshow -i audio='{}' -ar 44100 -ac 2".format(microphone)
    print(exe.format(e_a1 if enable_a1 else '', e_a2 if enable_a2 else '', bitrate, dir_))
    return powershell, exe.format(e_a1 if enable_a1 else '', e_a2 if enable_a2 else '', bitrate, dir_)


class MenuLabel(QLabel):
    signal = pyqtSignal()
    s2 = pyqtSignal()

    def __init__(self, tooltip):
        super(MenuLabel, self).__init__()
        self.setToolTip(tooltip)
        self.setAlignment(Qt.AlignCenter)

    def mouseReleaseEvent(self, ev: QtGui.QMouseEvent) -> None:
        if ev.button() == Qt.LeftButton:
            self.signal.emit()
        else:
            self.s2.emit()


class GlassWin(QFrame):
    def __init__(self, DIR):
        super(GlassWin, self).__init__()
        QToolTip.setFont(QFont('Ink Free'))
        self.icon = QIcon()

        self.dir = DIR
        self.icon.addPixmap(QPixmap(self.dir+'/icon.ico'))
        self.pause_output = list()
        self.setWindowIcon(self.icon)
        self.output = ''
        self.process = None
        self.mod = None
        self.status = 'stop'
        self.init_x = 0
        self.init_y = 0
        self.has_add_cam = False
        self.r = 20
        self.m_drag = False
        self.m_DragPosition = self.pos()
        self.setToolTip('FreeHe GlassCav')
        self.GF = GlassFile(read_pickle(DIR), DIR)
        self.GC = GlassCam()
        self.GV = GlassV(DIR, self)
        self.GA = GlassA(DIR, self)
        self.GAST = GlassAction('start', DIR)
        self.GASP = GlassAction('stop', DIR)
        self.GAP = GlassAction('pause', DIR)
        self.game_mod = MenuLabel('游戏模式')
        self.full_mod = MenuLabel('H264_QSV全屏模式')
        # self.sub_mod = MenuLabel('H264_QSV窗口模式')
        self.cam_add = MenuLabel('画中画摄像头')
        self.V = MenuLabel('视频参数:\n\th264 - Intel@ Quick Sync Video (VBR)\n\tFull Size, 30.00fps, format mp4')
        self.A = MenuLabel('音频参数:\n\tAAC: Advanced Audio Codeing\n\t48000HZ 1536kb/s')
        self.out_path = MenuLabel('输出路径<左键设置/右键打开>')
        self.pause = MenuLabel('暂停/开始')
        self.start = MenuLabel('开始录制')
        self.min = MenuLabel('最小化')
        self.close = MenuLabel('关闭')
        self.layout = QHBoxLayout()
        self.setFixedSize(700, 100)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet('''
            GlassWin {
                background-color: #202020;
            }
            MenuLabel:hover {
                border-width: 4px;
                border-color: #B81E06;
                border-style: solid;
            }
            QToolTip {
                background-color: #202020;
                padding: 20px;
                font-size: 30px;
                border-radius: 40px
            }
        ''')
        screen = QDesktopWidget()
        self.init_x = screen.width() - 900
        self.init_y = 100
        self.move(self.init_x, self.init_y)
        self.init_layout()
        self.setLayout(self.layout)
        self.init_signal()

    def chmod(self, mod):
        if self.status == 'start' or self.status == 'pause':
            return
        self.mod = mod
        print(self.mod)
        self.game_mod.setStyleSheet('''
            background-color: #202020;
        ''')
        self.full_mod.setStyleSheet('''
            background-color: #202020;
        ''')
        # self.sub_mod.setStyleSheet('''
        #     background-color: #202020;
        # ''')
        a = getattr(self, self.mod + '_mod')
        a.setStyleSheet('''
            background-color: #505050;
        ''')

    def init_signal(self):
        self.close.signal.connect(lambda: self.CLEAR())
        self.min.signal.connect(lambda: self.showMinimized())
        self.out_path.signal.connect(lambda: self.GF.show())
        self.out_path.s2.connect(lambda: QDesktopServices.openUrl(QUrl('file:///' + self.GF.input.text())))
        self.V.signal.connect(lambda: self.GV.show())
        self.A.signal.connect(lambda: self.GA.show())
        self.start.signal.connect(lambda: self.capturer())
        self.game_mod.signal.connect(lambda: self.chmod('game'))
        self.full_mod.signal.connect(lambda: self.chmod('full'))
        # self.sub_mod.signal.connect(lambda: self.chmod('sub'))
        self.cam_add.signal.connect(self.add_camera)
        self.pause.signal.connect(self.pause_event)

    def pause_event(self):
        if self.status == 'start':
            self.status = 'pause'
            self.pause.setPixmap(QPixmap(self.dir + '/icon/stop_.png'))
            self.stop_process()
            self.GAP.show_()
            return
        if self.status == 'pause':
            self.GAST.show_()
            self.status = 'start'
            self.pause.setPixmap(QPixmap(self.dir + '/icon/start_.png'))
            self.start_process()

    def restart(self):
        self.pause_event()
        time.sleep(1)
        self.pause_event()

    def CLEAR(self):
        self.GAP.destroy()
        self.GA.destroy()
        self.GAST.destroy()
        self.A.destroy()
        self.GASP.destroy()
        self.GC.destroy()
        self.GF.destroy()
        self.GV.destroy()
        self.hide()
        sys.exit()

    def init_layout(self):
        self.chmod('full')
        self.pause.setPixmap(QPixmap(self.dir + '/icon/stop_.png'))
        self.game_mod.setFixedSize(65, 65)
        self.game_mod.setProperty('name', 'game_mod')
        self.game_mod.setPixmap(QPixmap(self.dir + '/icon/game_mod.png'))
        self.full_mod.setFixedSize(65, 65)
        self.full_mod.setProperty('name', 'full_mod')
        self.full_mod.setPixmap(QPixmap(self.dir + '/icon/full_mod.png'))
        # self.sub_mod.setFixedSize(65, 65)
        # self.sub_mod.setProperty('name', 'sub_mod')
        # self.sub_mod.setPixmap(QPixmap(self.dir+'/icon/sub_mod.png'))
        self.cam_add.setFixedSize(65, 65)
        self.cam_add.setProperty('name', 'cam_add')
        self.cam_add.setPixmap(QPixmap(self.dir + '/icon/cam_add.png'))
        self.V.setFixedSize(65, 65)
        self.V.setProperty('name', 'V')
        self.V.setPixmap(QPixmap(self.dir + '/icon/V.png'))
        self.A.setFixedSize(65, 65)
        self.A.setProperty('name', 'A')
        self.A.setPixmap(QPixmap(self.dir + '/icon/A.png'))
        self.out_path.setFixedSize(65, 65)
        self.out_path.setProperty('name', 'out_path')
        self.out_path.setPixmap(QPixmap(self.dir + '/icon/file.png'))
        self.pause.setFixedSize(50, 50)
        self.pause.setProperty('name', 'pause')
        self.start.setPixmap(QPixmap(self.dir + '/icon/stop_.png'))
        self.start.setFixedSize(75, 75)
        self.start.setProperty('name', 'start')
        self.start.setPixmap(QPixmap(self.dir + '/icon/capturer.png'))
        self.min.setFixedSize(45, 45)
        self.min.setProperty('name', 'min')
        self.min.setPixmap(QPixmap(self.dir + '/icon/min.png'))
        self.close.setFixedSize(40, 40)
        self.close.setProperty('name', 'close')
        self.close.setPixmap(QPixmap(self.dir + '/icon/close.png'))
        self.layout.addWidget(self.game_mod)
        self.layout.addWidget(self.full_mod)
        # self.layout.addWidget(self.sub_mod)
        self.layout.addWidget(self.cam_add)
        self.layout.addWidget(self.V)
        self.layout.addWidget(self.A)
        self.layout.addWidget(self.out_path)
        self.layout.addWidget(self.pause)
        self.layout.addWidget(self.start)
        self.layout.addWidget(self.min)
        self.layout.addWidget(self.close)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.m_drag = True
            self.m_DragPosition = e.globalPos() - self.pos()
            e.accept()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.m_drag = False

    def mouseMoveEvent(self, e):
        if Qt.LeftButton and self.m_drag:
            self.move(e.globalPos() - self.m_DragPosition)
            e.accept()

    def add_camera(self):
        if not self.has_add_cam:
            self.cam_add.setStyleSheet('''
                background-color: #505050;
            ''')
            self.has_add_cam = True
            self.GC.show_()
            ...
        else:
            self.cam_add.setStyleSheet('''
                background-color: #202020;
            ''')
            self.has_add_cam = False
            self.GC.hide_()
            ...

    def capturer(self):
        if self.mod:
            if self.status == 'stop':
                self.status = 'start'
                self.GAST.show_()
                self.pause.setPixmap(QPixmap(self.dir + '/icon/start_.png'))
                self.start.setStyleSheet('''
                    background-color: #505050;
                ''')
                self.start_process()
                return
            elif self.status == 'start' or self.status == 'pause':
                self.status = 'stop'
                self.GASP.show_()
                self.pause.setPixmap(QPixmap(self.dir + '/icon/stop_.png'))
                self.start.setStyleSheet('''
                    background-color: #202020;
                ''')
                if self.process:
                    self.stop_process()
                if len(self.pause_output) == 1:
                    self.pause_output.clear()
                    return
                else:
                    print(self.GF.input.text() + '/concat.txt')
                    with open(self.GF.input.text() + '/concat.txt', 'w') as f:
                        for i in self.pause_output:
                            f.write('file ' + "'{}'\n".format(i))
                    time.sleep(1)
                    cmd = self.dir + '/dll/ffmpeg.exe -safe 0 -f concat -i {}/concat.txt -c copy '.format(
                        self.GF.input.text()) + self.GF.input.text() + '/' + str(int(time.time())) + '.mp4'
                    print(cmd)
                    concat = sp.Popen(cmd, shell=True)
                    print(self.pause_output)
                    concat.wait()
                    os.remove(self.GF.input.text() + '/concat.txt')
                    for i in self.pause_output:
                        os.remove(self.GF.input.text() + '/' + i)
                    self.pause_output.clear()
                return

    def start_process(self):
        self.output = str(int(time.time())) + '.mp4'
        self.pause_output.append(self.output)
        powershell, cmd = conf(self.dir, bitrate=self.GV.bit_rate.text() if self.mod != 'game' else '8000k',
                               enable_a1=self.GA.cb1.isChecked(), enable_a2=self.GA.cb2.isChecked(),
                               dir_=self.GF.input.text())
        cmd = cmd + '/' + self.output
        self.process = sp.Popen(cmd, shell=True, stdin=sp.PIPE, executable=powershell)

    def stop_process(self):
        time.sleep(0.5)
        self.process.stdin.write('e'.encode('gbk'))
        self.process = None
