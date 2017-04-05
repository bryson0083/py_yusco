import requests
import json
import time
import datetime
import pandas as pd
import sqlite3
import re
import os.path

from dateutil.parser import parse
from dateutil import parser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from random import randint

err_flag = False

#讀取帳密參數檔
with open('account.json') as data_file:
	data = json.load(data_file)

acc_id = data['lme']['id']
acc_pwd = data['lme']['pwd']

#print('acc=' + acc_id)
#print('pwd=' + acc_pwd)

# 登入頁面取得，__VIEWSTATE參數值
headers = {'User-Agent':'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'}

driver = webdriver.Chrome()
driver.get("https://www.metalprices.com/a/Login")

#輸入帳號密碼登入網站
elem = driver.find_element_by_name("Username")
elem.send_keys(acc_id)

elem = driver.find_element_by_name("Password")
elem.send_keys(acc_pwd)

driver.find_element_by_xpath("//input[@value='Login'][@class='login-button']").click()

#停頓隨機秒數
random_sec = randint(2,5)
time.sleep(random_sec)

#若有出現Switch Device按鈕，就點下去
title = driver.find_elements_by_xpath('//div[@class="title_div"]/h1')[0].text
#print(title)

if title == "Switch Device":
	driver.find_element_by_xpath("//input[@value='Switch Device']").click()

#若看到畫面抬頭是"Custom Dashboard - Tab 1"，表示登入成功並且切換設備成功
title = driver.find_elements_by_xpath('//div[@class="custom_dashboard_ctrls"]')[0].text
#print(title)

find_str_idx = title.find("Custom Dashboard - Tab 1")
#print(find_str_idx)

if find_str_idx > 0:
	driver.get("https://www.metalprices.com/dailyexchangedata/LMESummary/LME/LNI")

	#讀取報價table
	elem = driver.find_elements_by_xpath('//table[@class="high_low"]')[1]

	rdata = []	
	for tr in elem.find_elements_by_tag_name("tr"):
		td_data = []
		for td in tr.find_elements_by_tag_name("td"):
			td_data.append(td.text)
			#print(td.text)

		rdata.append(td_data)

	print(rdata)



time.sleep(60)

# 關閉瀏覽器視窗
driver.quit();