import requests
import time

from crawl.interruption_manager import interrupted

RETRY_TIME = 10
# 代理端口配置，Windows系统可通过“网络状态->代理->手动设置代理”找到代理端口，如未开启代理请忽略
# PROXY = {'http': '127.0.0.1:33210', 'https': '127.0.0.1:33210'}
PROXY = {}


def get_response(url, params=None):
    response = None
    while True:
        if interrupted():
            return None
        try:
            response = requests.get(url, params=params, proxies=PROXY)
            break
        except requests.exceptions.SSLError as e:
            print(f"[crawler] 网络错误，SSL证书错误，请关闭代理或配置crawler.py中的代理端口，{RETRY_TIME}秒后重试，错误信息：{e}")
            time.sleep(RETRY_TIME)
            continue
        except requests.exceptions.ConnectTimeout as e:
            print(f"[crawler] 网络错误，请求超时，{RETRY_TIME}秒后重试，错误信息：{e}")
            time.sleep(RETRY_TIME)
            continue
        except requests.exceptions.ConnectionError as e:
            print(f"[crawler] 网络错误，{RETRY_TIME}秒后重试，错误信息：{e}")
            time.sleep(RETRY_TIME)
            continue
    json_data = response.json()
    return json_data
