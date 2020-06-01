import socket
import re
import threading
import time
from Proxy.proxy import Proxy

"""
编码说明：斗鱼采用utf-8编码，所有字符用utf-8编码，但是使用urf-8解码其字节时却会出现字符集编码问题，一个方法是找到对应的字符集进行编码，
另一个设置decode()为非严格解码,strict='ingore',这里采用第二种
"""
gift_map={
    '20005': '超级火箭',
    '20004': '火箭',
    '20003': '飞机',
    '20010': 'MVP',
    '1859': '小飞船',
    '20417': '福袋',
    '2095': '幸运水晶',
    '20000': '鱼丸',
    '20002': '办卡',
    '20008': '超大丸星',
    '2097': '幸运戒指',
    '2096': '幸运钥匙',
    '20009': '天秀',
    '20001': '弱鸡',
    '20006': '点赞',
}
class douyuInfo:

    def __init__(self, room_id):
        self.port = 8601
        self.ip = 'openbarrage.douyutv.com'
        self.room_id = room_id
        self.st = socket.socket()
        self.gifts = []     # 存储获取到的礼物信息
        self.danmu = []     # 存储获取到的弹幕信息

    # 多线程运行，获取信息以及发送心跳信息
    def run(self):
        t1 = threading.Thread(target=self.get_info)
        t2 = threading.Thread(target=self.kepp_live)
        t1.start()
        t2.start()

    # 不断发送心跳信息，保持登录状态
    def kepp_live(self):
        while True:
            live = "type@=mrkl/\0".encode('utf-8')   # 新版客户端心跳信息
            self.send_msg(live)
            time.sleep(45)

    # 调用所有获取信息函数函数获取信息
    def get_info(self):
        if self.connect():   # 连接认证
            while True:
                content = self.st.recv(1024)
                gifts = self.get_gifts(content)  # 礼物信息
                danmus = self.get_danmu(content)  # 弹幕信息
                if gifts:
                    for gift in gifts:
                        if gift[0] in gift_map:
                            print(gift[1], '送出了礼物', gift_map[gift[0]])
                        else:
                            print(gift[1], '送出了礼物', gift[0])
                    self.gifts.extend(gifts)
                if danmus:
                    for danmu in danmus:
                        print('弹幕:', danmu)
                    self.gifts.extend(danmus)
        else:
            print('连接失败')

    # 登陆并入组房间
    def connect(self):
        try:
            self.st.connect((self.ip, self.port))
        except Exception as e:
            print('连接服务器失败', e.args)
            return False
        # 发送登陆授权消息  数据结尾是\0
        login = 'type@=loginreq/roomid@={}\0'.format(self.room_id).encode('utf-8')
        try:
            self.send_msg(login)
            print("连接服务端成功")
        except Exception as e:
            print("房间不存在......")
            return False
        # 发送入组信息
        joingroup = 'type@=joingroup/rid@={}/gid@=-9999/\0'.format(self.room_id).encode('utf-8')
        if self.send_msg(joingroup):
            print("入组房间成功")
        else:
            return False
        return True

    # 向服务端发送信息
    def send_msg(self, msg):
        # 构建协议头
        """
        1.协议头格式：消息长度，消息长度,消息类型，数据部分
        2.消息长度需要算上自身的长度，即消息本身的长度和消息长度的长度，发送了两遍，需要加上2*4
        3.消息类型不需要加上消息类型的长度
        4.以小端的方式转换
        5.使用sendall发送，递归发送直到全部发送完毕，成功返回none
        """
        msg_type = 689  # 消息类型
        msg_length = len(msg)+8
        head = int.to_bytes(msg_length, 4, byteorder='little') \
               + int.to_bytes(msg_length, 4, byteorder='little') \
               + int.to_bytes(msg_type, 4, byteorder='little')

        try:
            if self.st.sendall(head) == None:
                if self.st.sendall(msg) == None:
                    return True
                else:
                    print("消息发送失败")
            else:
                print("消息头发送失败")
            return False
        except Exception as e:
            # print(e.args)
            return False

    # 匹配礼物信息
    def get_gifts(self, content):
        pattern = re.compile(b'gfid@=(.*?)/')
        gift_id = pattern.findall(content)
        name = re.compile(b'nn@=(.*?)/').findall(content)
        gifts = []
        for i, j in zip(gift_id, name):   # 编码转换
            gifts.append((i.decode('utf-8', 'ignore'), j.decode('utf-8', 'ignore')))
        if gifts:
            return gifts
        return None

    def get_danmu(self, content):
        # 匹配弹幕消息
        pattern = re.compile(b'txt@=(.*?)/cid')
        danmu = pattern.findall(content)
        if danmu:
            danmu = [i.decode('utf-8', 'ignore') for i in danmu]
            return danmu
        return None


if __name__ == '__main__':
    print('请输入房间号')
    room_id = input()
    info = douyuInfo(room_id)
    info.run()




