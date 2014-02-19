#!/usr/bin/env python
#coding:utf-8

#feature to add
#todo:2 check login  done 
#todo 6:store pass?or store cookie
#todo:1 add get friendlist(name,etc) from login
#todo:3 support more than 2
#todo:4 add waiting indicator
#todo:5 onclick label goto browser
#http://www.cells.es/Members/srubio/howto/pyqt

import sys
from Queue import Queue
import re
from threading import Thread
import json
import cPickle
from PyQt4 import QtGui, QtCore, QtWebKit, QtNetwork
import requests
from bs4 import BeautifulSoup

result1 = str()

hd = {'Host': 'www.renren.com', 'Connection': 'keep-alive', 'Cache-Control': 'max-age=0',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Origin': 'http://www.renren.com',
      'User-Agent': ' Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36',
      'Content-Type': 'application/x-www-form-urlencoded', 'Referer': 'http://www.renren.com/SysHome.do',
      'Accept-Encoding': 'gzip,deflate,sdch', 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6'}

s = requests.Session()


class ClickableLabel(QtGui.QLabel):
    def __init__(self):
        super(QtGui.QLabel, self).__init__()
        self.show_cap()

    def mousePressEvent(self, QMouseEvent):
        self.show_cap()

    def show_cap(self):
        img = QtGui.QPixmap()
        img.loadFromData(s.get("http://icode.renren.com/getcode.do?t=web_login&rnd=Math.random()").content)
        self.setPixmap(img)


class LoginWindow(QtGui.QWidget):
    def __init__(self, father=None):
        super(QtGui.QWidget, self).__init__()
        self.father = father
        try:
            s.cookies = cPickle.load(open("./cookie", "rb"))
            s.get("http://www.renren.com")
            # print s.cookies.get_dict()
            self.father.show()
            return
        except Exception, e:
            print e.message

            pass
        s.get("http://www.renren.com/SysHome.do")
        self.setWindowTitle("Login")
        self.resize(204, 100)
        self.input_username = QtGui.QLineEdit()
        self.input_password = QtGui.QLineEdit()
        self.input_password.setEchoMode(QtGui.QLineEdit.Password)
        self.button_submit = QtGui.QPushButton("Login")
        self.button_submit.setShortcut(QtGui.QKeySequence.InsertParagraphSeparator)
        self.button_submit.clicked.connect(self.submit)
        self.button_remember = QtGui.QCheckBox("remember me?")

        self.lay = QtGui.QGridLayout()
        self.lay.addWidget(self.input_username)
        self.lay.addWidget(self.input_password)
        self.lay.addWidget(self.button_remember)
        self.setLayout(self.lay)
        # to get local stored info

        # self.cap = QtGui.QLabel()
        self.cap = ClickableLabel()
        self.lay.addWidget(self.cap)
        self.input_cap = QtGui.QLineEdit()
        self.lay.addWidget(self.input_cap)
        self.lay.addWidget(self.button_submit)
        self.show()

    def submit(self):

        if self.input_username.text().isEmpty() or self.input_password.text().isEmpty() or self.input_cap.text().isEmpty():
            QtGui.QMessageBox.warning(self, "Warning", "Input username/password/captcha")
            return False
        else:
            para = {"email": "%s" % str(self.input_username.text()), "password": "%s" % str(self.input_password.text()),
                    "icode": "%s" % str(self.input_cap.text()), "origURL": "http://www.renren.com/home",
                    "domain": "renren.com", "key_id": "1", "captcha_type": "web_login"}
            print para
            res = s.post("http://www.renren.com/PLogin.do", data=para, headers=hd)
            # ipython debug
            if res.history[0].content.find("failCode") != -1:
                QtGui.QMessageBox.warning(self, "Error", "Wrong Password/username/captcha")
                self.input_password.clear()
                self.input_cap.clear()
                self.cap.show_cap()
                return False
            else:
                if self.button_remember.checkState() != 0:
                    with open("./cookie", "wb") as f:
                        cPickle.dump(s.cookies, f)
                self.close()
                self.father.show()
                # self.parent().show()
                # m.exec_()
                # print "res"
                # print res.history
                # print res.history[0].content
                # if len(res.history)!=2:
                #     s.cookies.clear()
                #     return False
                # else:
                #     print "Here"
                #     self.close()
                #     m=MainWindow()
                #     m.show()
                #     return True


class MainWindow(QtGui.QWidget):
    # friends={}
    # fA=set()
    # fB=set()
    taskQueue = Queue()

    def __init__(self):
        super(QtGui.QWidget, self).__init__()
        self.setWindowTitle("RenrenCommandFriends")
        self.input_friendA = QtGui.QLineEdit()
        self.input_friendB = QtGui.QLineEdit()
        self.button_find = QtGui.QPushButton(u"Start")
        self.button_find.clicked.connect(self.work)
        self.lay = QtGui.QGridLayout()
        self.lay.addWidget(self.input_friendA)
        self.lay.addWidget(self.input_friendB)
        self.lay.addWidget(self.button_find)
        self.setLayout(self.lay)
        self.hide()
        self.login = LoginWindow(self)


    def work(self):
        if self.input_friendA.text().isEmpty() and self.input_friendA.text().isEmpty():
            QtGui.QMessageBox.warning(self, "Warning", "Input two friends")
            return False
        else:
            self.w = RenrenWorker(self.input_friendA.text(), self.input_friendB.text(), self)
            self.w.start()
            self.connect(self.w, QtCore.SIGNAL("ret(QString)"), self.display)

    def display(self, json_str):
        f = json.loads(str(json_str))
        for (k, v) in f.items():
            self.temp = QtGui.QLabel("<a href='http://www.renren.com/%s'>" % k + v[u"name"] + "</a>")
            self.temp.setOpenExternalLinks(True)
            self.lay.addWidget(self.temp)
        pass


class RenrenWorker(QtCore.QThread):
    friends = dict()
    commonfriends = dict()
    fA = set()
    fB = set()
    taskQueue = Queue()

    def __init__(self, f_a, f_b, parent):
        super(QtCore.QThread, self).__init__()
        self.fA_rid = f_a
        self.fB_rid = f_b
        try:
            fA_page, fB_page = self.get_page_num(self.fA_rid), self.get_page_num(self.fB_rid)
        except:
            QtGui.QMessageBox.warning(parent, "Error", u"出错了OOPS！")
            self.terminate()
            return
        for i in range(fA_page):
            self.taskQueue.put([self.fA_rid, i, self.fA])
        for i in range(fB_page):
            self.taskQueue.put([self.fB_rid, i, self.fB])
        pass


    def get_page_num(self, rid):
        return max(map(int, re.findall(r"GetFriendList\.do\?curpage=(\d*)", s.get(
            "http://friend.renren.com/GetFriendList.do?curpage=0&id=%s" % rid).content))) + 1


    def get_friend_info(self, rid, page, f_set):
        r = s.get("http://friend.renren.com/GetFriendList.do?curpage=%d&id=%s" % (page, rid))
        soup = BeautifulSoup(r.content)
        fs = soup.find(id="friendListCon")
        if fs.string == u'\n':
            return
        for i in fs.children:
            if i == "\n":
                continue
            rid = i.p.a['href'].split("=")[1]
            f_set.add(rid)
            pic = i.p.a.img.attrs['src']
            name = i.div.dl.dd.text.encode("utf-8")
            self.friends[rid] = {"avatar": pic, "name": name}

    def worker(self):
        while True:
            arg = self.taskQueue.get()
            self.get_friend_info(*arg)
            self.taskQueue.task_done()

    def run(self):
        for i in range(5):
            t = Thread(target=self.worker)
            t.setDaemon(True)
            t.start()
        self.taskQueue.join()
        for i in self.fA & self.fB:
            self.commonfriends[i] = self.friends[i]
        json_str = json.dumps(self.commonfriends)
        self.emit(QtCore.SIGNAL("ret(QString)"), json_str)
        self.terminate()
        pass

    def __del__(self):
        self.exiting = True
        self.wait()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    m = MainWindow()

    sys.exit(app.exec_())
