# 存储模块
MAX_SCORE = 100       # 代理分数
MIN_SCORE = 0
INITIAL_SCORE = 10    # 初始分数
REDIS_HOST = '127.0.0.1'   # redis参数
REDIS_PASSWORD = ''
REDIS_KEY = 'proxies'
REDIS_READY_KEY = 'ready_proxies'   #可用key
REDIS_PORT = '6379'

import redis
from random import choice   # choice(),返回列表或者元组之中的随即一个元素

"""
该类用于管理代理与redis数据库的增删获取等操作
"""
class RedisClient(object):
    # 初始化一个StrictRedis对象用于后面操作redis
    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD):
        try:
            # self.db = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True).flushdb()
            self.db = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True)
            print('连接成功')
        except:
            print("连接失败")


    # 添加一个代理，返回添加结果，设置初始分数
    # 注意redis.zadd参数传入字典形式
    def add(self, proxy,key = REDIS_KEY,score=INITIAL_SCORE):
        mapping = {
            proxy:score
        }
        if not self.db.zscore(key, proxy):  # 进行去重，判断该代理是否存在
            self.db.zadd(key, mapping)     # 向指定键值添加代理
            print("添加代理", proxy)

    # 获取一个可用的代理，先看是否有100分的，有了直接随机返回，没有了按照分数顺序返回，
    def get_proxy(self):
        result = self.db.zrangebyscore(REDIS_READY_KEY, MAX_SCORE, MAX_SCORE)   # 返回指定区间指定键值的结果
        if len(result):
            return choice(result)
        else:
            result = self.db.zrangebyscore(REDIS_READY_KEY, 0, 100)   # 根据score进行排名，可用代理极少，故获取全部
            if len(result):
                return choice(result)
            else:
                print("无可用代理")
                return None

    # 减少代理相对应的分数
    def decrease(self,key,proxy):
        score = self.db.zscore(key, proxy)
        if score and score > MIN_SCORE:   # 未达到阈值，减分
            print("代理", proxy, '当前分数', score, '减一')
            return self.db.zincrby(key, proxy, -1)  # 对指定键值对应代理的分数+ （-1）
        else:   # 达到阈值，移除该代理
            print("代理", proxy, '移除')
            return self.db.zrem(key, proxy)

    # 判断代理是否存在
    def exists(self,key,proxy):
        if self.db.zscore(key, proxy):
            return True
        return False

    # 将代理设置为可用，即更改分数为100
    def max(self,proxy):   #专门给 200 代理用的  故无需传key
        print('代理', proxy, '设置为可用')
        return self.add(proxy,REDIS_READY_KEY, MAX_SCORE)   # 根据键名对应zset添加 代理，设置分数维100(存在则更改分数)

    # 获取当前代理的数量
    def count(self):
        return self.db.zcard(REDIS_KEY)

    # 获取全部代理
    def get_all(self,key):
        return self.db.zrangebyscore(key, MIN_SCORE, MAX_SCORE)

