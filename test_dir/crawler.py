# 这里定义一些别的模块用到的函数
import requests
from requests import exceptions
from bs4 import BeautifulSoup

def get_html(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.75 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            raise exceptions.ConnectionError
    except:
        return None

# 获取模块

""""
这里先是定义一个元类，用于对代理进行抽取，整合代理获取方法，之后定义一个类，并设置元类，
该类用于获取各种代理，
...感觉对于这里的元类什么的还是不是很理解
"""


class ProxyMetaclass(type):
    def __new__(mcs, name, bases, attrs):
        count = 0       # 记录函数的个数
        attrs['__CrawlFunc__'] = []    # 将所有获取代理方法整合为一个属性
        # items()方法遍历字典的所有属性，k为键值，v为具体的值
        for k, v in attrs.items():
            if 'crawl_' in k:
                attrs['__CrawlFunc__'].append()
                count += 1
        attrs['__CrawlFuncCount__'] = count
        return type.__new__(mcs, name, bases, attrs)   # 返回一个对象


# 爬虫获取类
# 这里如果在元类里面定义属性的话，后面莫名奇妙无法访问，所以这里手动在init里面定义了方法
class Crawler(object):
    def __init__(self):
        count = 0
        self.__CrawlFunc__ = []
        self.__CrawlFunc__.extend(['crawl_kuaidaili'])
        self.__CrawlFuncCount__ = 1

    # 获取所有代理站点的代理
    def get_proxies(self, callback):
        proxies = []
        # 传入代理点，通过eval拼接表达式执行相应方法,相当于调用了相应的代理方法
        for proxy in eval("self.{}()".format(callback)):   #字符串转列表
            proxies.append(proxy)  # 返回生成器类型，所以这里用append
        print("成功获取代理", callback)
        return proxies


    # 获取kuaidaili网站的代理，传入总页数
    def crawl_kuaidaili(self, page_count=500):
        base_url = 'https://www.kuaidaili.com/free/inha/{}'   # 这里很简单，就是构造url,查找ip,返回生成器
        urls = [base_url.format(page) for page in range(1, page_count)]
        for url in urls:
            html = get_html(url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                table = soup.find(class_='table')
                trs = table.find_all('tr')[1:]
                for tr in trs:
                    tds = tr.find_all('td')
                    ip = tds[0].text
                    port = tds[1].text
                    yield ':'.join([ip, port])

    # 爬取西刺代理网站的代理
    def crawl_xicidaili(self, page_count=10):
        base_url = 'https://www.xicidaili.com/nn/{}'
        urls = [base_url.format(page) for page in range(1,500)]
        for url in urls:
            html = get_html(url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                table = soup.find(id='ip_list')
                trs = table.find_all('tr')[1:]
                for tr in trs:
                    tds = tr.find_all('td')
                    ip = tds[1].text
                    port = tds[2].text
                    yield ':'.join([ip, port])

    # 爬取89网站的代理
    def crawl_89daili(self, page_count=20):
        base_url = 'http://www.89ip.cn/index_{}.html'
        urls = [base_url.format(page) for page in range(1, page_count)]
        for url in urls:
            html = get_html(url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                table = soup.find(class_='layui-table')
                trs = table.find_all('tr')[1:]
                for tr in trs:
                    tds = tr.find_all('td')
                    ip = tds[0].text.strip()
                    port = tds[1].text.strip()
                    yield ':'.join([ip, port])

