# -*-coding=utf-8-*-
import os
import re
import datetime
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_argument('lang=zh_CN.UTF-8')  # 设置中文
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
chrome_options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
chrome_options.add_argument('--headless')  # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
# 设置手机请求头 （手机页面反爬虫能力稍弱）
chrome_options.add_argument('Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Mobile Safari/537.36')


driver_path=r"/usr/bin/chromedriver"
browser = webdriver.Chrome(executable_path=driver_path, options=chrome_options)

class fetch_list():
    def __init__(self, base, url, **kwargs):
        self.base=base
        self.url = base+url
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }

    def run(self):
        browser.get(self.url)
        soup=BeautifulSoup(browser.page_source, 'html.parser')
        # print(soup.prettify())

        # 抓取当前页面的链接
        items=soup.select('font.newslist_style > a', limit=3)
        for item in items:
            suburl=item.get('href')
            fetch_page(self.base, suburl).run()

        # 如果有下一页则继续抓取
        # next_page=soup.find_all("a", text="下一页", limit=1)
        # if len(next_page) > 0:
        #     # print(next_page)
        #     next_page_url=next_page[0].get('tagname')
        #     # print(next_page_url)
        #     fetch_list(self.base, next_page_url).run()


class fetch_page():
    def __init__(self, base, url, **kwargs):
        self.base=base
        self.url = base+url
        self.headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        }

    def run(self):
        print(self.url)
        browser.get(self.url)
        soup=BeautifulSoup(browser.page_source, 'html.parser')
        # print(soup.prettify())

        items=soup.select('td.content > div')
        datetime=soup.select('span#shijian')
        date=datetime[0].get_text().split(" ", 1)[0]
        year=date.split("-", 1)[0]
        # print(items)

        fo=open("data/huobi/"+year+"/huobi-"+date+".html", "w")
        fo.write(str(items[0]))



# '''run'''
# if __name__ == '__main__':
#     base = os.environ["HUOBI_BASE"]
#     url = os.environ["HUOBI_URL"]
#     sign_in = fetch_list(base, url)
#     sign_in.run()


'''run'''
if __name__ == '__main__':
    base = 'http://www.pbc.gov.cn'
    url = '/zhengcehuobisi/125207/125213/125431/125475/index.html'
    
    sign_in = fetch_list(base, url)
    sign_in.run()
    

    browser.close()
    browser.quit()
