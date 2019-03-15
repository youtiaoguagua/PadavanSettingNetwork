# -*- coding: utf-8 -*-
from PyQt5 import QtCore,QtWidgets
from PyQt5.QtCore import pyqtSignal, QEventLoop, QTimer,QThread

import sys
from win32com.client import GetObject

import paramiko

from untitled6 import Ui_MainWindow

import requests


class BackendThread(QThread):
    update_date = pyqtSignal()

    def run(self):
        while True:
            self.update_date.emit()
            loop = QEventLoop()
            QTimer.singleShot(5000, loop.quit)
            loop.exec_()


class MyWindow(QtWidgets.QMainWindow,Ui_MainWindow):
    _signal = QtCore.pyqtSignal(str)


    def __init__(self, parent=None):
        super(MyWindow, self).__init__(parent=parent)
        self.setupUi(self)

        self.pushButton.clicked.connect(self.clicks)
        self._signal.connect(self.TextToDisplay)
        self.xiancheng()

    def xiancheng(self):
        self.backend = BackendThread()
        self.backend.update_date.connect(self.getip)
        self.backend.start()

    def getip(self):
        try:
            result = requests.get("http://ip.6655.com/ip.aspx",timeout=1)
            self.what_ip.setText("联网IP:"+result.text)
        except:
            self.what_ip.setText("无法检测网络")



    def clicks(self):
        wmi = GetObject('winmgmts:/root/cimv2')
        while 1:
            processes = wmi.ExecQuery(
                "Select * from Win32_NTLogEvent where Logfile = 'Application' and EventCode = '20221'")
            self.c=''
            for process in processes:
                a = process.InsertionStrings[5]

                self.c = a.split('\n')[1].split('\r')[1]


                break
            if self.c != '':
                break

        self._signal.emit("截获:"+self.c)
        self.mySignal()

    def ssh2(self):
        ip = self.three.text()

        username = self.four.text()

        passwd = self.five.text()
        self.cmd = "sed -i \'2,3c user \"{user}\"\\npassword \"{password}\"\' /tmp/ppp/options.wan0&/usr/sbin/pppd file /tmp/ppp/options.wan0&/usr/sbin/pppd plugin xinjiang_qinghai_sxplugin.so".format(user=self.c,password=self.two.text())

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, 22, username, passwd, timeout=5)
            stdin, stdout, stderr = ssh.exec_command(self.cmd)
            # print(stdout.read())
            self._signal.emit("路由连接成功!,开始执行so文件")
            ssh.close()
            loop = QEventLoop()
            QTimer.singleShot(500, loop.quit)
            loop.exec_()
            self._signal.emit("执行完毕，请检查网络！")
            # self.getip()

        except:
            self._signal.emit("连接路由失败！请检查网络连接，和连接信息！")



    def mySignal(self):
        self._signal.emit('开始执行，请稍后！')
        self.ssh2()

    def TextToDisplay(self,str):
        loop = QEventLoop()
        QTimer.singleShot(500, loop.quit)
        loop.exec_()
        self.textBrowser.append(str)



if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MyWindow()
    w.show()
    sys.exit(app.exec_())
