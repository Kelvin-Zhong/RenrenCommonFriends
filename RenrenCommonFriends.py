import sqlite3
import requests
import os
from bs4 import BeautifulSoup
import re
import sys
from Queue import Queue
from threading import Thread
import time


# hd={'Host':'www.renren.com','Connection':'keep-alive','Cache-Control':'max-age=0','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8','Origin':'http://www.renren.com','User-Agent':' Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.107 Safari/537.36','Content-Type':'application/x-www-form-urlencoded','Referer':'http://www.renren.com/SysHome.do','Accept-Encoding':'gzip,deflate,sdch','Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6'}
#
# para={"email":"%s"%name,"password":"%s"%password,"icode":"","origURL":"http://www.renren.com/home","domain":"renren.com","key_id":"1","captcha_type":"web_login"}

n=time.time()

friends={}
fB=set()
fA=set()
taskQueue=Queue()

g_cookie=os.environ['localappdata']+"\\Google\\Chrome\\User Data\\Default\\Cookies"

conn=sqlite3.connect(g_cookie)
conn.row_factory=sqlite3.Row
cur=conn.cursor()
cur.execute("SELECT name,value FROM cookies WHERE host_key like '.renren.com'")
res=cur.fetchall()
cookie={}
for i in res:
    if i['name'] in cookie:
        continue
    cookie[i['name']]=i['value']

# print cookie
# sys.exit()


def get_page_num(rid):
    return max(map(int,re.findall(r"GetFriendList\.do\?curpage=(\d*)",s.get("http://friend.renren.com/GetFriendList.do?curpage=0&id=%s"%rid,cookies=cookie).content)))+1

def get_friend_info(rid,page,f_set):
    r=s.get("http://friend.renren.com/GetFriendList.do?curpage=%d&id=%s"%(page,rid),cookies=cookie)
    soup=BeautifulSoup(r.content)
    fs=soup.find(id="friendListCon")
    if fs.string==u'\n':
        return
    for i in fs.children:
        if i=="\n":
            continue
        rid=i.p.a['href'].split("=")[1]
        f_set.add(rid)
        pic=i.p.a.img.attrs['src']
        name=i.div.dl.dd.text.encode("utf-8")
        friends[rid]={"avatar":pic,"name":name}

def worker():
    while True:
        arg=taskQueue.get()
        get_friend_info(*arg)
        taskQueue.task_done()





s=requests.Session()

if len(sys.argv)!=3:
    sys.exit()

fA_rid,fB_rid=sys.argv[1],sys.argv[2]
fA_page,fB_page=get_page_num(sys.argv[1]),get_page_num(sys.argv[2])

for i in range(fA_page):
    taskQueue.put([fA_rid,i,fA])

for i in range(fB_page):
    taskQueue.put([fB_rid,i,fB])



for i in range(5):
    t=Thread(target=worker)
    t.setDaemon(True)
    t.start()

taskQueue.join()

for f in fA&fB:
    print friends[f]["name"]

print "----------------------"
print len(fA&fB)
print time.time()-n







