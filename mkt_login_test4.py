# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 13:14:53 2017

@author: bryson0083
chcp 65001
"""
import requests
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

import time

#讀取帳密參數檔
with open('account.json') as data_file:
	data = json.load(data_file)

acc_id = data['custeel']['id']
acc_pwd = data['custeel']['pwd']
	
#print('acc=' + acc_id)
#print('pwd=' + acc_pwd)

# 登入頁面取得，__VIEWSTATE參數值
headers = {'User-Agent':'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'}

driver = webdriver.Chrome()
driver.get("http://www.custeel.com/")

#網頁查詢條件輸入，並提交表單
elem = driver.find_element_by_name("username")
elem.send_keys(acc_id)

elem = driver.find_element_by_name("password")
elem.send_keys(acc_pwd)

driver.find_element_by_xpath("//input[@type='image'][@class='img']").click()



time.sleep(5)

