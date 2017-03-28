# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 13:14:53 2017

@author: bryson0083
chcp 65001
"""

import LoginWebSite
import sys
import requests
from bs4 import BeautifulSoup

err_flag = False
s = requests.session()
headers = {'User-Agent':'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'}

#登入網站
Login_CNCCM = LoginWebSite.Login_CNCCM(s)
print(Login_CNCCM)

if Login_CNCCM == False:
	#登入失敗直接結束程式
	sys.exit("登入中華商務網失敗!")


URL = 'http://www.chinaccm.com/PriceInfo/InfoView.aspx?id=262801_1620129'
r = s.get(URL, headers=headers)
r.encoding = "utf-8"
sp = BeautifulSoup(r.text, 'html.parser')
#print(sp)

table = sp.findAll('table', attrs={'class':'priceinfo_tab'})

rdata = [[td.text for td in row.select('td')]
		 for row in table[0].select('tr')]

print(rdata)
