# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 13:14:53 2017

@author: bryson0083
"""

import LoginWebSite
import sys
import requests
from bs4 import BeautifulSoup

err_flag = False
s = requests.session()

#登入網站
login_mtp = LoginWebSite.Login_MTP(s)

if login_mtp == False:
	#登入失敗直接結束程式
	sys.exit("登入metalprices.com網站失敗!")

headers = {'User-Agent':'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'}
URL = 'https://www.metalprices.com/dailyexchangedata/LMESummary/LME/LNI'

payload = {
		"Unit": "MT",
		"Currency": "usd"
		}

r = s.post(URL, data=payload, headers=headers)
r.encoding = "utf-8"

sp = BeautifulSoup(r.text, 'html.parser')
table = sp.findAll('table', attrs={'class':'high_low'})
#print(table)

#網頁分成上下兩個報表，要抓的是第二個報表
rdata = [[td.text for td in row.select('td')]
				for row in table[1].select('tr')]

#排除空的list元素
data = []
for row in rdata:
	if len(row) > 0:
		data.append(row)


print(data)

#登出網站
#LoginWebSite.Logout_LME(s)
