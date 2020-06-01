
#from tkinker import *

#mpl.use('TkAgg')
#import matplotlib.pyplot as plt
from pylab import *
from matplotlib import pyplot as plt
from  matplotlib import cm
from matplotlib.font_manager import FontProperties
import numpy as np

import pymysql

password = '111111'

font = FontProperties(fname=r"/usr/share/fonts/wqy-zenhei/wqy-zenhei.ttc", size=14)

class Obj():
    def __init__(self):
        self.title = []
        self.pre = []
        self.hot = []
        self.ave = []
        self.playNum = []
        self.now = []
        self.time_map = {}

    def GetList(self,table):
        db = pymysql.connect("localhost", "root", password, "douyu")
        cursor = db.cursor()
        sql = "SELECT * FROM %s" % table

        if table == 'DOUYU':
            try:
                cursor.execute(sql)
                result = cursor.fetchall()
                for obj in result:
                    self.title.append(obj[0])
                    self.playNum.append(obj[1])
                    self.hot.append(obj[2])
                    self.pre.append(obj[3])
                    self.ave.append(obj[4])
            except:
                print("Error: unable to fetch data")
        else:
            try:
                cursor.execute(sql)
                result = cursor.fetchall()
                for obj in result:
                    self.title.append(obj[0])
                    self.playNum.append(obj[1])
                    self.hot.append(obj[2])
                    self.now.append(str(obj[3]))
                #   print(obj[3])
            except:
                print("Error: unable to fetch data")

        db.close()
        l = len(result)

        return l

    def GetView(self, len, p0, p1, p2, num,leftTitle="斗鱼当前&&统计热度"):


        fig = plt.figure(num)  # 定义一个长20宽20的画布
        ax = fig.add_subplot(111)

        x = np.arange(len)
        plt.bar(x, p0, width=0.25)
        plt.title('斗鱼热度状况', size=20, loc='right',fontproperties=font)

        ax.set_ylabel(leftTitle,fontproperties=font)
        ax.set_xlabel("各模块",fontproperties=font)


        if p1.__len__() != 0:
            plt.bar(x + 0.25, p1, width=0.25)

        plt.xticks(x, self.title, rotation=-90, size=8)

        #  plt.legend(prop={'family':'SimHei','size':20})  # 设置题注

        ax1 = ax.twinx()  # this is the important function
        ax1.set_ylabel("开播人数",fontproperties=font)
        ax1.plot(x, p2, color='b')

        plt.show()
        plt.close()

def GetBing(time_map,num):
    """
        绘制饼图
        explode：设置各部分突出
        label:设置各部分标签
        labeldistance:设置标签文本距圆心位置，1.1表示1.1倍半径
        autopct：设置圆里面文本
        shadow：设置是否有阴影
        startangle：起始角度，默认从0开始逆时针转
        pctdistance：设置圆内文本距圆心距离
        返回值
        l_text：圆内部文本，matplotlib.text.Text object
        p_text：圆外部文本
        """
    lens = len(time_map)
    for key,value in list(time_map.items()):
        if value == 0:
            del time_map[key]
    fig = plt.figure(num,figsize=(10,10))
    plt.title('斗鱼热度分布', size=20, loc='center', fontproperties=font)

    colors = cm.rainbow(np.arange(lens)/lens)

    label_list = []
    size = []
    explode = []
    i=0.01
    for key,value in time_map.items():

        label_list.append(key)
        size.append(value)
        explode.append(i)
        i+=(0.1-0.01)/lens
    #label_list = time # 各部分标签
   # size =   # 各部分大小
  #  color = ["r", "g", "b"]  # 各部分颜色
   # explode = [0.05, 0, 0]  # 各部分突出值
    plt.pie(size,labels=label_list,explode=explode,labeldistance=1, autopct='%1.1f%%',colors=colors)
    plt.legend(loc="upper right",fontsize=10,bbox_to_anchor=(1.1,1.05),borderaxespad=0.3)

    plt.show()
    plt.close()


def GetTime_Map(time_map):
    for i in range(25):
        if i == 24:
            break
        key = str(i) + ":00-" + str(i) +":30"
        time_map[key] = 0
        key1 = str(i) + ":30-" + str(i+1) +":00"
        time_map[key1] = 0

   # print(time_map)

def GetMap_Value(time_map,now):

    for item in now:
        values = item.split(':')
     #   print(values)
        if int(values[1])-30>=0:
            key = values[0] + ":30-" + str(int(values[0])+1) +":00"
            time_map[key] +=1
        else:
            key = values[0] + ":00-" + str(values[0]) + ":30"
            time_map[key] +=1

def Run_View():
# if __name__ == '__main__':

    # while True:
    obj = Obj()
    len1 = obj.GetList('DOUYU')

    obj.GetView(len1, obj.hot, obj.pre, obj.playNum, 1)  # 获取热度和统计热度的直方图 以及 直播人数的折线图
    obj.GetView(len1, obj.ave, [], obj.playNum, 2,"平均热度")  # 获取统计热度和直播人数的直方图和折线图  进行对比

    obj1 = Obj()
    len2 = obj.GetList('DOUYUHot')
    GetTime_Map(obj.time_map)
    GetMap_Value(obj.time_map, obj.now)
    GetBing( obj.time_map, 3)
        #time.sleep(72000)

