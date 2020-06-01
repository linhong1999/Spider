# 这里定义一些别的模块用到的函数
import requests
from requests import exceptions
from .db import RedisClient

def get_html(url):
    proxy = RedisClient().get_proxy()
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
