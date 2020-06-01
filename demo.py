import requests
from bs4 import BeautifulSoup
import re
import json
import time
import pymysql
import threading
import view
from Proxy.db import RedisClient


douYu_Map = {
    'LOL':'2_1', 'How':'2_2', 'CSGO':'2_6', 'dota2rpg':'2_650','WOW':'2_5','DOTA':'2_217','FTG':'2_29',
    'jdqs':'2_270', 'mszb':'2_55','classic':'2_26','qqfcdy':'2_375','Overwatch':'2_148','JX3':'2_65',
    'DOTA2':'2_3', 'blzy':'2_347','TVgame':'2_19','NEWGAME':'2_665','BF':'2_466','qzsg':'2_497','qjfs':'2_478',
    'CF':'2_33', 'gwlrsj':'2_367','wzry':'2_181','hpjy':'2_350','yiqilaizhuoyao':'2_545','zzq':'2_663',
    'DNF':'2_40', 'chichao':'2_709','phone':'2_30','qipai':'2_113','hyrz':'2_196','qqfcsy':'2_331','CFSY':'2_178',
    'APEX':'2_651', 'wpzs':'2_634','xyzx':'2_229','PPKDCSY':'2_654','yys':'2_240','LRS':'2_260','xingyu':'2_287','ecy':'2_174',
    'HW':'2_124','ms':'2_194','music':'2_175','xiangye':'2_662','yqk':'2_208','HDJY':'2_646','smkj':'2_134','yj':'2_195',
    'kepu':'2_204','rwjs':'2_212','car':'2_136','jlp':'2_514','BLOVES':'2_283','IMC':'2_750','FM233':'2_405','yydt':'2_422',
    'lianmaihudong':'2_441','qinggan':'2_447','PlayGame':'2_435','znl':'2_250',
    'directory/sport/cate':'2_-1','famine':'2_23','mhls':'2_524','wqzs':'6_634',
    'yz':'rknc/directory/yzRec','tianya':'2_59','jw3zjjh':'2_631',
}

headers ={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36"
    }

password = '111111'

class Obj:
    def __init__(self,title = '',pre = 0,hot = 0,ave = 0,playNum = 0,pageNum = 0):

        self.title = title
        self.pre = pre   #当前热度
        self.hot = hot   #统计热度
        self.ave = ave   #平均热度
        self.playNum = playNum
        self.pageNum = pageNum
        self.now = time.strftime('%H:%M:%S',time.localtime())

    def Create(self):
        db = pymysql.connect("localhost", "root", password, "douyu")
        cursor = db.cursor()
        cursor.execute("DROP TABLE IF EXISTS DOUYU")

        sql = """CREATE TABLE DOUYU(
                game CHAR(50) PRIMARY KEY ,
                playNum INT ,
                hot FLOAT ,
                pre FLOAT ,
                ave FLOAT 
        )ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;"""

        cursor.execute(sql)
        db.close()

    def GetHot(self,url_dir):
        getCursor = Cursor()   #跑一次开一次
        self.Create()
        for key, value in url_dir.items():
            obj = Obj()
            obj.title = key
            print(obj.title)
            soup = GetHtml(value)
            k = soup.find_all(class_='layout-Partition-info')

            if k[1].text == '0':
                continue

            print("当前热度:" + k[0].text)
            print("开播人数:" + k[1].text)
            obj.pre = float(re.sub("万", "", k[0].text))

            if "万" not in k[0].text:  # 若热度小于一万
                obj.pre /= 10000

            playNum = (int)(k[1].text)
            obj.playNum = playNum
            pageNum = (int)(playNum / 120)  # 分页
            obj.pageNum = pageNum + 1
            watch_num = 0
            for i in range(1, obj.pageNum + 1):

                if obj.title != "yz":
                    detail_url = 'https://www.douyu.com/gapi/rkc/directory/' + douYu_Map[obj.title] + '/' + str(i)
                else:
                    detail_url = 'https://www.douyu.com/gapi/rknc/directory/yzRec' + '/' + str(i)

                err_data = requests.get(detail_url).text
                object = json.loads(err_data)

                for j in range(0, len(object['data']['rl'])):
                    watch_num += int(object['data']['rl'][j]['ol'])

                obj.hot = watch_num / 10000

            obj.ave = obj.hot / obj.playNum

            print("统计热度:%.2f" % obj.hot + "万")
            print("平均热度:%.2f" % obj.ave + "万")
            getCursor.Save(obj)
            getCursor.Sum(obj)

        getCursor.Close_db()    #跑完一次关一次

    def Run_Hot(self):
        url = "https://www.douyu.com/directory/all"
        times = 1
        try:
            while True:
                times+=1
                url_dir = GetDir(GetHtml(url))
                self.GetHot(url_dir)
                time.sleep(1800)
                if times ==48 :   #一天清一次数据
                    print("清除数据中ZZZzzz")
                    times = 1
                    self.CreateHot()
                    self.Create()
                    time.sleep(5)

        except Exception as e:
            print("Run Hot error", e.args)

    def Run_Them(self):
        t = threading.Thread(target=self.Run_Hot)
      #  t1 = threading.Thread(target=view.Run_View)
        t.start()
       # t1.start()

    def CreateHot(self):  # 每个小时跑，统计

        db = pymysql.connect("localhost", "root", password, "douyu")
        cursor = db.cursor()
        cursor.execute("DROP TABLE IF EXISTS DOUYUHot")
        sql = """CREATE TABLE DOUYUHot(
                    game CHAR(50) PRIMARY KEY,
                    playNum INT ,
                    hot FLOAT,
                    now TIME
            )ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;"""

        cursor.execute(sql)

        db.close()

class Cursor():
    def __init__(self):

        self.db = pymysql.connect("localhost", "root", password, "douyu")
        self.cursor = self.db.cursor()
    def Close_db(self):
        self.db.close()

    def Save(self,obj):
        game = str(obj.title)
        playNum = obj.playNum
        hot = float(obj.hot)
        pre = float(obj.pre)
        ave = float(obj.ave)

        sql = """INSERT INTO DOUYU(game,playNum,hot,pre,ave)
                VALUE('%s','%d','%f','%f','%f') """ % (game, playNum, hot, pre, ave)

        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()
    def SaveHot(self,obj):

        print(obj.now)

        sql = """INSERT INTO DOUYUHot(game,playNum,hot,now)
                VALUE('%s','%d','%f','%s') """ % (obj.title,obj.playNum, obj.hot, obj.now)
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            self.db.rollback()

    def Sum(self,obj):  # 统计最高热度每生成一个对象，统计一次

        sql = "SELECT * FROM DOUYUHot where game = '%s'" % obj.title
        try:
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            if result:
                for item in result:
                    if item[2] <= obj.hot:
                        sql = "UPDATE DOUYUHot SET PlayNum = '%d' , hot = '%f' , now = '%s' WHERE game = '%s' " \
                              % (obj.playNum, obj.hot, obj.now, obj.title)
                        self.cursor.execute(sql)
                        try:
                            self.cursor.execute(sql)
                            self.db.commit()
                        except:
                            self.db.rollback()
            else:
                self.SaveHot(obj)
        except:
            print("Error: unable to fetch data")

def clearSession():
    s = requests.session()      #http连接太多   关闭
    s.keep_alive = False
    print('打开http太多，正在重试')

def GetHtml(url):
    try:
      #   proxy = RedisClient().get_proxy()
      # #  print(proxy)
      #   proxies = {
      #       'http': 'http://' + proxy,
      #       # 'https': 'https://' + proxy
      #   }
        try:
            requests.adapters.DEFAULT_RETRIES = 5        #增加重连次数
            r = requests.get(url, headers=headers,  timeout=10)
            # r = requests.get(url, headers=headers, proxies=proxies ,timeout = 10)
        except:
            clearSession()
            GetHtml(url)

        r.raise_for_status()
        demo = r.text
        soup = BeautifulSoup(demo, "lxml")
        # print(soup.prettify())
        return soup
    except Exception as e:
        print("Html error",e.args)

def GetDir(soup):

    url_dir = {}
    len = 0
    p = re.compile(r'/g_.*$')
    p1 = re.compile(r'.*$')
    for i in soup.find(class_ = 'Aside-menu'):
        for k in i:
            for a in k.find_all('a'):
                link = a.get('href')     #print(link)
                result = p.findall(link)
                if result:
                    key = p1.match(result[0],3)
                    len+=1
                    url_dir[key.group()] = "https://www.douyu.com" + result[0]
    return url_dir

if __name__ == "__main__":
    obj = Obj()
    obj.Run_Them()

