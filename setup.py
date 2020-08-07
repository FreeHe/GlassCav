# ----------------------------------
# author : FreeHe
# github : https://github.com/FreeHe
# ----------------------------------
import subprocess
import sys
import zipfile
import os

from PyQt5.QtWidgets import QApplication

from GlassEffects import GlassFile

setup_dir = os.getcwd()


class GS(GlassFile):
    def __init__(self):
        super(GS, self).__init__('', os.getcwd())
        self.setup_dir = os.getcwd()
        self.input.setPlaceholderText('请选择安装路径')
        self.input.setEnabled(False)
        self.vbs = info = '''
                        cwd = "{}"
                        d1 = "regsvr32 /s " & cwd & "/dll//audio_sniffer-x64.dll"
                        d2 = "regsvr32 /s " & cwd & "/dll//screen-capture-recorder-x64.dll"
                        set fs =createobject("scripting.filesystemobject")
                        set f=fs.opentextfile(cwd & "\cmd.bat",2, true)
                        f.writeline d1
                        f.writeline d2
                        f.close
                    
                        Set shell = CreateObject("Shell.Application")
                        shell.ShellExecute cwd & "/cmd.bat", "","","runas",0
                    
                        Set WshShell=WScript.CreateObject("WScript.Shell")
                        strDesktop=WshShell.SpecialFolders("Desktop")
                        set oShellLink = WshShell.CreateShortcut(strDesktop & "\GlassCav.lnk")
                        oShellLink.TargetPath = cwd & "\GlassCav\GlassCav.exe"
                        oShellLink.WindowStyle = 1
                        oShellLink.Hotkey = ""
                        oShellLink.IconLocation = cwd & "\GlassCav\GlassCav.exe, 0"
                        oShellLink.Description = ""
                        oShellLink.WorkingDirectory = cwd & "\GlassCav"
                        oShellLink.Save
                    
                        WScript.Quit
                    '''.format(setup_dir)

    def check_dir(self):
        if os.path.isdir(self.input.text()):
            z = zipfile.ZipFile(self.setup_dir + '/GlassCav.zip')
            os.mkdir(self.input.text() + '/GlassCav')
            z.extractall(self.input.text() + '/GlassCav')
            with open(self.input.text() + '/shell.vbs', 'w') as f:
                f.write(self.vbs)
            sp = subprocess.Popen(self.input.text() + '/shell.vbs', shell=True)
            sp.wait()
            sys.exit()


app = QApplication(sys.argv)
w = GS()
w.show()
sys.exit(app.exec_())

