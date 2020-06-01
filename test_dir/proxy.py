"""
定时获取，检测代理
"""
from .getter import Getter
from .tester import Tester
from multiprocessing import Process
import time
Tester_Run = False
Getter_Run = True
class Proxy():
    # def __init__(self):
    #     self.tester = Tester()
    #     self.getter = Getter()

    # 检测代理
    def proxy_tester(self):
        while True:
            print('进行测试')
            Tester().run()
            time.sleep(30)

    # 获取代理
    def proxy_getter(self):
        while True:
            print("抓取代理")
            Getter().run()
            time.sleep(30)

    def run(self):
        print("代理池开始运行")
        if Tester_Run:
            tester_process = Process(target=self.proxy_tester)
            tester_process.start()
        if Getter_Run:
            getter_process = Process(target=self.proxy_getter)
            getter_process.start()



