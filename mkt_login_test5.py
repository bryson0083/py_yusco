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
Login_CNFEOL = LoginWebSite.Login_CNFEOL(s)
print(Login_CNFEOL)

if Login_CNFEOL == False:
	#登入失敗直接結束程式
	sys.exit("登入cnfeol網站失敗!")

"""
URL = 'http://www.51bxg.com/web/data_center/coil_price_list.aspx?type=卷&mkt=佛山市场&mat=304&transactionstatus=切边&start_date=&end_date=&surf=No.1&fac=太钢不锈'

r = s.get(URL, headers=headers)
r.encoding = "utf-8"
sp = BeautifulSoup(r.text, 'html.parser')

table = sp.findAll('table', attrs={'class':'dc_data_list'})

rdata = [[td.text for td in row.select('td')]
		 for row in table[0].select('tr')]

print(rdata)
"""