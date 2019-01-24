import re
import time

import pymongo
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from lxml import etree
from urllib.parse import quote

MONGO_URL = 'localhost'
MONGO_DB = 'facebook'
# browser = webdriver.Chrome()
# browser = webdriver.PhantomJS(service_args=SERVICE_ARGS)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--proxy-server=socks5://127.0.0.1:1080")
browser = webdriver.Chrome(chrome_options=chrome_options)

wait = WebDriverWait(browser, 10)
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

base_url = 'https://www.facebook.com/pg'
KEYWORDS = ['python','java','c++','Mac','Liunx','Facebook']


def login():
    browser.get('https://www.facebook.com')
    browser.find_element_by_id('email').send_keys('')　# facebook邮箱
    browser.find_element_by_id('pass').send_keys('')　# 密码
    browser.find_element_by_id('login_form').submit()
    browser.implicitly_wait(10)


def search_key(KEYWORD):
    url = 'https://www.facebook.com/search/str/' + quote(KEYWORD) + '/keywords_pages?epa=SEE_MORE'
    browser.get(url)
    while 1:
        time.sleep(6)
        js = "var q=document.documentElement.scrollTop=10000"
        browser.execute_script(js)
        if '已经到底啦' in browser.page_source:
            break

    doc = etree.HTML(browser.page_source)
    divs = doc.xpath("//a[@class='_32mo']/@href")
    for url in divs:
        parse(url)

def index_page():
 
    # 抓取索引页
    print('---------')
    try:
        # js = "var q=document.documentElement.scrollTop=10000"
        # browser.execute_script(js)
        doc = etree.HTML(browser.page_source)
        divs = doc.xpath("//a[@class='_32mo']/@href")
        for url in divs:
            parse(url)
        # submit = wait.until(
        #     EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager div.form > span.btn.J_Submit')))
        # input.clear()
        # input.send_keys(page)
        # submit.click()
        # wait.until(
        #     EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#mainsrp-pager li.item.active > span'), str(page)))
        # wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.m-itemlist .items .item')))
        #
    except TimeoutException:
        index_page()

def parse(url):

    browser.get(url)
    doc = etree.HTML(browser.page_source)
    jianjie = base_url + doc.xpath("//div[@class='_2yaa' and contains(@data-key,'tab_about')]/a/@href")[0]
    browser.get(jianjie)
    time.sleep(2)
    doc = etree.HTML(browser.page_source)
    # ret = re.compile(r'<div class="_50f4">(.*?@.*?)</div>')
    # results = re.findall(ret,browser.page_source)
    results = doc.xpath("//div[@class='_50f4']/text()")
    if len(results) > 0:
        for result in results:
            if '@' in result:
                print(result)


def scroll_until_loaded():
    el = browser.find_element_by_id("facebook")
    js = "var q=document.documentElement.scrollTop=10000"
    browser.execute_script(js)
    time.sleep(2)
    browser.execute_script(js)
    time.sleep(2)
    browser.execute_script(js)
    time.sleep(2)
    print(browser.page_source)
    # check_height = browser.execute_script("return document.body.scrollHeight;")
    # while True:
    #     browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #     try:
    #         wait.until(
    #             lambda driver: browser.execute_script("return document.body.scrollHeight;") > check_height)
    #         check_height = browser.execute_script("return document.body.scrollHeight;")
    #     except TimeoutException:
    #         break

def close():
    browser.close()

def main():
    login()
    for key in KEYWORDS:
        search_key(key)
    close()


if __name__ == '__main__':
    main()
