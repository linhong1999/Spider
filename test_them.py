# 存储模块
# MAX_SCORE = 100       # 代理分数
# MIN_SCORE = 0
# INITIAL_SCORE = 10    # 初始分数
# REDIS_HOST = '127.0.0.1'   # redis参数
# REDIS_PASSWORD = ''
# REDIS_KEY = 'proxies'     #测试key
# REDIS_READY_KEY = 'ready_proxies'   #可用key
# REDIS_PORT = '6379'
#
# import redis
# from random import choice   # choice(),返回列表或者元组之中的随即一个元素
#
# # class RedisClient(object):
# #     # 初始化一个StrictRedis对象用于后面操作redis
# #     def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD):
# #         try:
# #             self.db = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True)
# #             print('连接成功')
# #         except:
# #             print("连接失败")
# #     def get_proxy(self):
# #         result = self.db.zrangebyscore(REDIS_READY_KEY, MAX_SCORE-10, MAX_SCORE)   # 返回指定区间指定键值的结果
# #         if len(result):
# #             print('可用代理')
# #             return choice(result)
# #         else:
# #             result = self.db.zrangebyscore(REDIS_READY_KEY, 0, 100)   # 根据score进行排名，返回前一百个元素
# #             if len(result):
# #                 print('几率可用代理')
# #                 # print(len(result))
# #                 return choice(result)
# #             else:
# #                 print("无可用代理")
# #                 return None

import aiohttp
from test_dir.db import RedisClient
import asyncio


MAX_CONCURRENCE = 46
class Tester():
    def __init__(self):
        self.redis = RedisClient()
        self.url = 'https://www.xaut.club'   # 测试url
        self.REDIS_KEY = 'proxies'     #测试key
        self.REDIS_READY_KEY = 'ready_proxies'   #可用key
        self.access_count = 0
        self.count = 0
    # 定义异步函数检测代理
    async def test_proxy(self, proxy):
        aiohttp.TCPConnector(verify_ssl=False)   # 不进行ssl证书检测，这样url前面都用http,不用https 防止ssl报错
        async with aiohttp.ClientSession() as session:
            try:
                proxy = proxy
                print("测试代理", proxy)
                async with session.get(self.url, proxy='http://' + proxy, timeout=10) as session:  #异步requests
                    self.count +=1
                    if session.status == 200:
                        self.access_count+=1
                    else:
                        pass
            except Exception:  #timeout 异常
                self.count += 1
                print('请求失败')
            if self.count == MAX_CONCURRENCE:
                return print('请求总次数为:',self.count,'其中成功:',self.access_count)

    # 测试所有代理函数
    # 创建事件循环，将代理测试放入事件之中
    def run(self):
        print("开始测试所有代理")
        try:
            proxies = self.redis.get_all(self.REDIS_READY_KEY)
            loop = asyncio.get_event_loop()   # 创建事件循环
            now_proxies = proxies[0: MAX_CONCURRENCE]
            tasks = [self.test_proxy(proxy) for proxy in now_proxies]  # 模拟 now_proxies 次请求
            loop.run_until_complete(asyncio.wait(tasks))
            # for i in range(0, len(proxies)):
            #     now_proxies = proxies[i:i+100]
            #     tasks = [self.test_proxy(proxy) for proxy in now_proxies]   #模拟 now_proxies 次请求
            #     loop.run_until_complete(asyncio.wait(tasks))
            #     #该方法类型于线程中的join方法，asyncio.wait()可以接受一个可以迭代的对象
            #     time.sleep(4)       # 一次检测100个
        except Exception as e:
            print('测试错误...', e.args)

if __name__ == '__main__':
    concurrence = Tester()
    concurrence.run()