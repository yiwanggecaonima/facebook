
from selenium import webdriver
from sockshandler import SocksiPyHandler
import socks
from urllib.request import build_opener
from lxml import etree
import pymongo
import time
import re

class Road():
    def __init__(self):
        self.base_url = 'http://silkroad4n7fwsrw.onion/'
        self.conn = pymongo.MongoClient('127.0.0.1',27017)
        self.db = self.conn['Road']

        self.chromeOptions = webdriver.ChromeOptions()

        # 设置代理　这是selenium设置代理的格式
        self.chromeOptions.add_argument("--proxy-server=socks5://127.0.0.1:9150")
        # 一定要注意，=两边不能有空格
        self.browser = webdriver.Chrome(chrome_options=self.chromeOptions)
        self.browser.get(self.base_url)
        time.sleep(20)
        print(self.browser.page_source)
        self.proxy_handler = SocksiPyHandler(proxytype=socks.SOCKS5, proxyaddr='127.0.0.1', proxyport=9150)
        self.opener = build_opener(self.proxy_handler)


    def get_all(self,response):
        # 登录碰到验证码
        if 'CAPTCHA' in response:
            img = r'<img src="(.*?)" />'
            img_link = re.findall(img,response)[0]
            print(img_link)
            img_html = self.opener.open(img_link,timeout=40).read()
            with open('captcha.png','wb') as f:
                f.write(img_html)

            rr = self.browser.find_element_by_xpath("//form/input[1]")
            key = input('keys:')
            rr.send_keys(key)
            submit = self.browser.find_element_by_xpath("//form/input[2]")
            submit.click()
            # time.sleep(30)
            self.get_all(response)
        else:
            doc = etree.HTML(response)
                # print(doc)
            # divs = doc.xpath("//tr/td[1]/div[@id='vp']//tr/td[2]/div")
            # # print(divs)
            # for div in divs:
            #     link = div.xpath("./a[1]/@href")[0]
            #
            #     title = div.xpath("./a[1]/text()")[0]
            #     Price = div.xpath("./b[2]/text()")[0].rstrip('/')
            #     view_list = div.xpath("./a[2]/@href")[0]
            #     Category = div.xpath("./a[3]/text()")[0]
            #     ShipsFrom= div.xpath("./span[@id='ah_ships']/text()")[0]
            #     print(title,Price,link,view_list,Category,ShipsFrom,sep='\n')
            #     print('\n\n')
            divs = doc.xpath("//tr/td[2]/div[@id='vp']/a/@href")
            for div in divs:
                sub_link = self.base_url + div
                print(sub_link)
                self.browser.get(sub_link)
                time.sleep(15)
                self.get_content(self.browser.page_source)
                
     # 解析并保存到mongodb
    def get_content(self,response):
        # self.browser.get(link)
        doc = etree.HTML(response)
        divs = doc.xpath("//tr/td[1]/div[@id='vp']//tr/td[2]/div")
        if divs:
            # print(divs)
            for div in divs:
                item = {}

                item['link'] = self.base_url +  div.xpath("./a[1]/@href")[0]

                item['title'] = div.xpath("./a[1]/text()")[0]
                item['Price'] = div.xpath("./b[2]/text()")[0].rstrip(' /')
                item['view_list'] = self.base_url + div.xpath("./a[2]/@href")[0]
                item['Category'] = self.base_url +  div.xpath("./a[3]/text()")[0]
                item['ShipsFrom'] = div.xpath("./span[@id='ah_ships']/text()")[0]
                # print(title,Price,link,view_list,Category,ShipsFrom,sep='\n')
                print(item)
                print('\n\n')
                if self.db['SilkRoad'].insert(item):
                    print('Sueecss saved to Mongo ...... ')
                else:
                    print('FAILED')
                    
        while True:
            try:
                next_link = self.browser.find_element_by_xpath("//tr/td[1]/center/form/input[@value='Next Page']")
                if next_link:
                    next_link.click()
                    time.sleep(10)
                    self.get_content(self.browser.page_source)
            except Exception:

                return None

    def web(self):
        # 这里会出现验证码，如果玩机器学习的小伙伴也可以试试用tensorflow或者sklearn进行图像识别，难度应该不大，但是过程估计不轻松
        if 'CAPTCHA' in self.browser.page_source:
            img = r'<img src="(.*?)" />'
            img_link = re.findall(img,self.browser.page_source)[0]
            print(img_link)
            img_html = self.opener.open(img_link,timeout=40).read()
            with open('captcha.png','wb') as f:
                f.write(img_html)

            rr = self.browser.find_element_by_xpath("//form/input[1]")
            key = input('keys:')
            rr.send_keys(key)
            submit = self.browser.find_element_by_xpath("//form/input[2]")
            submit.click()
            # time.sleep(30)
            self.get_all(self.browser.page_source)
        else:
            self.get_all(self.browser.page_source)
        # 退出，清除浏览器缓存
        self.browser.quit()

    def run(self):
        self.web()

if __name__ == '__main__':
    r = Road()
    r.run()

