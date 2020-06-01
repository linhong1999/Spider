# 获取代理并存储到数据库当中

from .db import RedisClient
from .crawler import Crawler

MAX_CRWLER = 10000

class Getter(object):
    def __init__(self):
        self.crawler = Crawler()       # 代理类和存储类
        self.redis = RedisClient()

    # 判断代理池是否达到上限，这里可以根据情况指定
    def is_full(self):
        if self.redis.count() > MAX_CRWLER:
            return True
        return False

    # 获取并存储操作
    def run(self):
        print("获取代理中...")
        if not self.is_full():
            # 传入所有获取代理的函数名
            for callback_number in range(self.crawler.__CrawlFuncCount__):  #range(3)
                callback = self.crawler.__CrawlFunc__[callback_number]
                proxies = self.crawler.get_proxies(callback)
                for proxy in proxies:
                    self.redis.add(proxy)

