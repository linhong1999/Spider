
"""
测试模块，
1.对数据库当中的代理不断进行测试，更新分数，可用将分数设置为100，不可用分数--，
2.测试代理是否可用时，采用异步库aiohttp测试，使用代理访问百度网站，返回值为200则代表代理可用
3.同步库requests请求时会阻塞进程，程序向下执行直到接收到响应，如果请求时间过长，检测效率会很低，
所以使用异步库aiohttp,异步发送所有请求，之后接受响应，不会阻塞进程，而是执行其他的循环体，提高效率，
"""
import aiohttp
from .db import RedisClient
import asyncio
import time

class Tester():
    def __init__(self):
        self.redis = RedisClient()
        self.url = 'http://www.baidu.com'   # 测试url
        self.REDIS_KEY = 'proxies'     #测试key
        self.REDIS_READY_KEY = 'ready_proxies'   #可用key

    # 定义异步函数检测代理
    async def test_proxy(self, proxy):
        aiohttp.TCPConnector(verify_ssl=False)   # 不进行ssl证书检测，这样url前面都用http,不用https 防止ssl报错
        async with aiohttp.ClientSession() as session:
            try:
                proxy = proxy
                print("测试代理", proxy)
                async with session.get(self.url, proxy='http://' + proxy, timeout=10) as session:  #异步requests
                    if session.status == 200:
                        self.redis.max(proxy)
                    else:
                        self.redis.decrease(self.REDIS_KEY,proxy)
            except Exception:  #timeout 异常
                self.redis.decrease(self.REDIS_KEY,proxy)
                print('请求失败')

    # 测试所有代理函数
    # 创建事件循环，将代理测试放入事件之中
    def run(self):
        print("开始测试所有代理")
        try:
            proxies = self.redis.get_all(self.REDIS_KEY)
            loop = asyncio.get_event_loop()   # 创建事件循环
            for i in range(0, len(proxies)):
                now_proxies = proxies[i:i+100]
                tasks = [self.test_proxy(proxy) for proxy in now_proxies]   #模拟 now_proxies 次请求
                loop.run_until_complete(asyncio.wait(tasks))
                #该方法类型于线程中的join方法，asyncio.wait()可以接受一个可以迭代的对象
                time.sleep(4)       # 一次检测100个
        except Exception as e:
            print('测试错误...', e.args)
