#!/usr/bin/env python
#coding:utf-8

#feature to add
#todo:2 check login  done 
#todo 6:store pass?or store cookie almost done
#todo:1 add get friendlist(name,etc) from login need yours id almost done
#todo:5 onclick label goto browser almost done
#to fix:1 when adding combobox item ,gui react slow.
#to fix:2 when serach for the second time,the previous result haven't been removed.
#to fix:3 logical fault about rid may need block before Mainwindow after login window  =>change rid logic to mainwindow
#todo:3 support more than 2
#todo:4 add waiting indicator
#todo:7 improve the interface
#http://www.cells.es/Members/srubio/howto/pyqt

import sys
import os
from Queue import Queue
import re
from threading import Thread
import json
import cPickle
from PyQt4 import QtGui, QtCore
import requests
from bs4 import BeautifulSoup


hd = {'Host': 'www.renren.com', 'Connection': 'keep-alive', 'Cache-Control': 'max-age=0',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Origin': 'http://www.renren.com',
      'User-Agent': ' Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36',
      'Content-Type': 'application/x-www-form-urlencoded', 'Referer': 'http://www.renren.com/SysHome.do',
      'Accept-Encoding': 'gzip,deflate,sdch', 'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6'}

s = requests.Session()


class ClickableLabel(QtGui.QLabel):
    def __init__(self):
        super(ClickableLabel, self).__init__()
        self.show_cap()

    def mousePressEvent(self, QMouseEvent):
        self.show_cap()

    def show_cap(self):
        img = QtGui.QPixmap()
        img.loadFromData(s.get("http://icode.renren.com/getcode.do?t=web_login&rnd=Math.random()").content)
        self.setPixmap(img)


class LoginWindow(QtGui.QWidget):
    def __init__(self, father=None):
        super(LoginWindow, self).__init__()
        self.setWindowIcon(QtGui.QIcon(""))
        self.father = father
        try:
            s.cookies = cPickle.load(open("./cookie", "rb"))
            content=s.get("http://www.renren.com")
            if content.history==[]:
                QtGui.QMessageBox.warning(self,"Warning","Cookie is expired,Please relogin")
                try:
                    os.remove("./cookie")
                except:
                    pass
            # print s.cookies.get_dict()
            else:
                self.rid=s.cookies.get("id")
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
            # print para
            res = s.post("http://www.renren.com/PLogin.do", data=para, headers=hd)
            if res.history[0].content.find("failCode") != -1:
                QtGui.QMessageBox.warning(self, "Error", "Wrong Password/username/captcha")
                self.input_password.clear()
                self.input_cap.clear()
                self.cap.show_cap()
                return False
            else:
                self.rid=s.cookies.get("id")
                if self.button_remember.checkState() != 0:
                    with open("./cookie", "wb") as f:
                        cPickle.dump(s.cookies, f)
                self.close()
                self.father.show()




class MainWindow(QtGui.QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.login = LoginWindow(self)

        #temparorily remove friendlist functions
        # self.rid=self.login.rid
        # self.gw=GetFriendWorker(self.rid)
        # self.gw.start()
        # self.connect(self.gw,QtCore.SIGNAL("retFriend(QString)"),self.appendFriends)

        self.setWindowTitle("RenrenCommandFriends")
        self.resize(640,480)
        self.select_friendA=QtGui.QComboBox()
        self.select_friendB=QtGui.QComboBox()
        self.input_friendA = QtGui.QLineEdit()
        self.input_friendB = QtGui.QLineEdit()
        self.select_friendA.setLineEdit(self.input_friendA)
        self.select_friendB.setLineEdit(self.input_friendB)
        self.select_friendA.addItem("",QtCore.QVariant())
        self.select_friendB.addItem("",QtCore.QVariant())
        self.button_find = QtGui.QPushButton(u"Start")
        self.button_find.clicked.connect(self.start)
        self.lay = QtGui.QGridLayout()
        self.lay.addWidget(self.select_friendA,0,0)
        self.lay.addWidget(self.select_friendB,0,3)
        self.lay.addWidget(self.button_find,0,1)
        self.friendlistlayout=QtGui.QGridLayout()
        self.lay.addLayout(self.friendlistlayout,1,0)
        self.setLayout(self.lay)
        # self.hide()





    def appendFriends(self,json_str):
        f=json.loads(str(json_str))
        for (k,v) in f.items():
            self.select_friendA.addItem(v[u"name"],QtCore.QVariant(k))
            self.select_friendB.addItem(v[u"name"],QtCore.QVariant(k))
        pass

    def start(self):
        if self.input_friendA.text().isEmpty() and self.input_friendA.text().isEmpty():
            QtGui.QMessageBox.warning(self, "Warning", "Input two friends")
            return False
        else:
            if self.select_friendA.currentIndex()>0:
                self.fA=self.select_friendA.itemData(self.select_friendA.currentIndex()).toString()
            else:
                self.fA=self.input_friendA.text()

            if self.select_friendB.currentIndex()>0:
                self.fB=self.select_friendB.itemData(self.select_friendB.currentIndex()).toString()
            else:
                self.fB=self.input_friendB.text()
            self.w = RenrenWorker(self.fA,self.fB, self)
            self.w.start()
            self.connect(self.w, QtCore.SIGNAL("ret(QString)"), self.display)

    def display(self, json_str):
        f = json.loads(str(json_str))
        for (k, v) in f.items():
            self.temp = QtGui.QLabel("<a href='http://www.renren.com/%s'>" % k + v[u"name"] + "</a>")
            self.temp.setOpenExternalLinks(True)
            self.friendlistlayout.addWidget(self.temp)
            self.temp=QtGui.QLabel()
            img = QtGui.QPixmap()
            img.loadFromData(s.get(v[u"avatar"]).content)
            self.temp.setPixmap(img)
            self.friendlistlayout.addWidget(self.temp)

        pass

    #self.connect(self,signal("xxx"),self.newComp)
    def newComplte(self,qlist):
        self.complter=QtGui.QCompleter(qlist)
        self.select_friendA.setCompleter(self.complter)
        self.select_friendB.setCompleter(self.complter)


class GetFriendWorker(QtCore.QThread):
    queue=Queue()
    def __init__(self,rid):
        super(QtCore.QThread,self).__init__()
        self.rid=rid
        pages=RenrenWorker.get_page_num(self.rid)
        for i in range(pages):
            self.queue.put(i)
        pass

    def run(self):
        for i in range(5):
            t = Thread(target=self.worker)
            t.setDaemon(True)
            t.start()
        self.queue.join()

        # self. emit(signal(newComplete(Stringlist),...))
        pass

    def worker(self):
        while True:
            arg = self.queue.get()
            self.get_friend_info(arg)
            self.queue.task_done()

    def get_friend_info(self,arg):
        r = s.get("http://friend.renren.com/GetFriendList.do?curpage=%d&id=%s" % (arg, self.rid))
        soup = BeautifulSoup(r.content)
        fs = soup.find(id="friendListCon")
        if fs.string == u'\n':
            return
        for i in fs.children:
            if i == "\n":
                continue
            rid = i.p.a['href'].split("=")[1]
            pic = i.p.a.img.attrs['src']
            name = i.div.dl.dd.text.encode("utf-8")
            self.emit(QtCore.SIGNAL("retFriend(QString)"),json.dumps({rid:{"avatar": pic, "name": name}}))




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
        except Exception,e:
            print e.message
            QtGui.QMessageBox.warning(parent, "Error", u"出错了OOPS！")
            self.terminate()
            return
        for i in range(fA_page):
            self.taskQueue.put([self.fA_rid, i, self.fA])
        for i in range(fB_page):
            self.taskQueue.put([self.fB_rid, i, self.fB])
        pass

    @staticmethod
    def get_page_num(rid):
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
