# -*- coding: utf-8 -*-
"""
Created on Tue Sep 20 21:51:06 2022

@author: carlo
"""

import pandas as pd
import numpy as np
from datetime import datetime 
import streamlit as st
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from time import sleep
import requests
from lxml import etree
from bs4 import BeautifulSoup

# to run selenium in headless mode (no user interface/does not open browser)
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument("--disable-gpu")
options.add_argument("--disable-features=NetworkService")
options.add_argument("--window-size=1920x1080")
options.add_argument("--disable-features=VizDisplayCompositor")

keywords = 'anker'

driver = Chrome(options=options)
# driver.get('https://shopee.ph/search?keyword=' + keywords)
delay = 4
# prods = driver.find_elements(By.XPATH, '//div[@class="col-xs-3 shopee-search-item-result__item"]')

# html = requests.get('https://shopee.ph/search?keyword=' + keywords)
# soup = BS4(html.content, 'html.parser')
# dom = etree.HTML(str(soup))
# print(dom.xpath('div[@class="ie3A+n bM+7UW Cve6sh"]'))


# WebDriverWait(driver, delay)
# print("Page is ready")
# sleep(delay)
# html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
# soup = BeautifulSoup(html, "html.parser")

def shopee_get_html(driver, keywords, page=0, delay=5):
    driver.get('https://shopee.ph/search?keyword=' + keywords + '&page=' + str(page))
    WebDriverWait(driver, delay)
    sleep(delay)
    html = driver.execute_script("return document.getElementsByTagName('html')[0].innerHTML")
    soup = BeautifulSoup(html, "html.parser")
    # check if error page
    error_page = len(soup.find_all('div', class_="shopee-search-empty-result-section__title"))
    
    return soup, error_page
    
item_name, item_price, item_sold, item_loc, item_link = [], [], [], [], []
page, error = 0,0

# while "no results found page" is not present:
soup, error = shopee_get_html(driver = driver,
                            keywords = keywords,
                            page = page,
                            delay = delay)
while error != 1:
    print (f'Collecting products from page {page}')
    # scroll to end of page to make all products visible
    last_height = driver.execute_script("return document.documentElement.scrollHeight")
    while True:
        #driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
        print ("Scrolling..")
        sleep(2)
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        print ("new_height: {}".format(new_height))  
        if new_height == last_height:
            print ("Finished scrolling!")
            break
        else:
            pass
        last_height = new_height
    for item_ in soup.find_all('div', class_='KMyn8J'):
        name = item_.find_all('div', class_='ie3A+n bM+7UW Cve6sh')
        price = item_.find_all('div', class_='hpDKMN')
        sold = item_.find_all('div', class_='r6HknA uEPGHT')
        loc = item_.find_all('div', class_='zGGwiV')
        # name
        if name != []:
            item_name.append(name[0].get_text())
        else:
            item_name.append("None")
        # price
        if price != []:
            item_price.append(price[0].get_text())
        else:
            item_price.append("None")
        # items sold
        if sold != []:
            item_sold.append(sold[0].get_text())
        else:
            item_sold.append("None")
        # location
        if loc != []:
            item_loc.append(loc[0].get_text())
        else:
            item_loc.append("None")
        # product link
        #item_link.append("shopee.ph/" + str(item_.find_all('a')['href']))
    print (f'Found {len(item_name)} items')
    # next page
    page += 1
    soup, error = shopee_get_html(driver = driver,
                                  keywords = keywords,
                                  page = page,
                                  delay = delay)
    
# convert to dataframe
df_prod = pd.DataFrame({'item_name': item_name, 
                        'item_price': item_price, 
                        'item_sold': item_sold,
                        'item_loc': item_loc})
