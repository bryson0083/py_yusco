# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 13:14:53 2017

@author: bryson0083
chcp 65001
"""
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

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from random import randint

import LoginWebSite

def Read_CUSTEEL():

	err_flag = False

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

	#輸入帳號密碼登入網站
	elem = driver.find_element_by_name("username")
	elem.send_keys(acc_id)

	elem = driver.find_element_by_name("password")
	elem.send_keys(acc_pwd)

	driver.find_element_by_xpath("//input[@type='image'][@class='img']").click()

	#停頓隨機秒數
	random_sec = randint(2,5)
	time.sleep(random_sec)

	###########################################################################

	#開啟報價網頁(304/NO.1)
	print("開啟報價網頁，讀取 304 NO.1 報價資料.\n")
	driver.get("http://www.custeel.com/s1013/1013_more.jsp?group=1013004&cat=1006001&area=1001004001008")
	driver.find_element_by_xpath("//a[contains(text(),'佛山地区304/NO.1卷板参考价')]").click()

	#停頓等待
	time.sleep(2)

	#Focus到新的分頁
	driver.switch_to_window(driver.window_handles[1])

	#取得報表抬頭
	title = driver.find_elements_by_xpath('//div[@id="share1"]/h1')[0].text
	#print(title)

	# 取得報表抬頭日期
	#title = '3月14日佛山地区304/NO.1卷板参考价'
	result = re.split("\D+", title)

	rls_title = []
	for element in result:
		rls_title.append(element)

	#只取出前兩個代表月與日的參數
	rls_title = rls_title[0:2]
	#print(rls_title)

	ls_title = []
	for element in rls_title:
		len_elem = len(element)
		if len_elem == 1:
			element = "0" + element
		ls_title.append(element)

	#print(ls_title)
	
	yyyy = str(datetime.datetime.now().year)
	title_dt_no1 = yyyy + ls_title[0] + ls_title[1]	#報表抬頭日期
	#print("抬頭日期=" + title_dt_no1)

	#讀取報價table
	table_id = driver.find_element(By.ID, 'main_c')

	rdata = []
	for rows in table_id.find_elements(By.TAG_NAME, "tr"):
		td = [elm.text for elm in rows.find_elements(By.TAG_NAME, "td")]
		rdata.append(td)

	df = pd.DataFrame(rdata[1:], columns = rdata[0])
	#print(df)

	#過濾需要的資料
	df_no1 = pd.DataFrame()
	for i in range(0,len(df)):
		spec = df['规格'][i]
		factor = df['产地'][i]
		price = int(df['价格'][i]) - 200	#扣掉200元，轉為毛邊價

		if spec == "4.0*1500*C":
			if factor == "太钢":
				tk_price_no1 = price
			elif factor == "宝钢":
				bao_price_no1 = price
			elif factor == "鞍钢联众":
				lz_price_no1 = price

	data = {'dt': title_dt_no1, \
			'tk_price_no1': tk_price_no1, \
			'bao_price_no1': bao_price_no1, \
			'lz_price_no1': lz_price_no1 \
			}
	df_no1 = pd.DataFrame(data, index=[0])
	print(df_no1)

	#關閉分頁
	driver.close();

	#Focus到主頁面
	driver.switch_to_window(driver.window_handles[0])

	###########################################################################

	#開啟報價網頁(304/2B)
	print("開啟報價網頁，讀取 304 2B 報價資料.\n")
	driver.get("http://www.custeel.com/s1013/1013_more.jsp?group=1013004&cat=1006001&area=1001004001008")
	driver.find_element_by_xpath("//a[contains(text(),'佛山地区304/2B卷板参考价')]").click()

	#停頓等待
	time.sleep(2)

	#Focus到新的分頁
	driver.switch_to_window(driver.window_handles[1])

	#取得報表抬頭
	title = driver.find_elements_by_xpath('//div[@id="share1"]/h1')[0].text
	#print(title)

	# 取得報表抬頭日期
	#title = '3月14日佛山地区304/2B卷板参考价'
	result = re.split("\D+", title)

	rls_title = []
	for element in result:
		rls_title.append(element)

	#只取出前兩個代表月與日的參數
	rls_title = rls_title[0:2]
	#print(rls_title)

	ls_title = []
	for element in rls_title:
		len_elem = len(element)
		if len_elem == 1:
			element = "0" + element
		ls_title.append(element)

	#print(ls_title)
	
	yyyy = str(datetime.datetime.now().year)
	title_dt_2b = yyyy + ls_title[0] + ls_title[1]	#報表抬頭日期
	#print("抬頭日期=" + title_dt_2b)

	#讀取報價table
	table_id = driver.find_element(By.ID, 'main_c')

	rdata = []
	for rows in table_id.find_elements(By.TAG_NAME, "tr"):
		td = [elm.text for elm in rows.find_elements(By.TAG_NAME, "td")]
		rdata.append(td)

	df = pd.DataFrame(rdata[1:], columns = rdata[0])
	#print(df)

	#過濾需要的資料
	df_2b = pd.DataFrame()
	for i in range(0,len(df)):
		spec = df['规格'][i]
		factor = df['产地'][i]
		price = int(df['价格'][i]) - 200	#扣掉200元，轉為毛邊價

		if spec == "2.0*1219*C":
			if factor == "太钢":
				tk_price_2b = price
			elif factor == "宝新":
				bx_price_2b = price
			elif factor == "鞍钢联众":
				lz_price_2b = price

	data = {'dt': title_dt_2b, \
			'tk_price_2b': tk_price_2b, \
			'bx_price_2b': bx_price_2b, \
			'lz_price_2b': lz_price_2b \
			}
	df_2b = pd.DataFrame(data, index=[0])
	print(df_2b)

	###########################################################################
	
	#判斷兩報價抓取的抬頭日期，若不相同，則提示錯誤，並結束
	if title_dt_no1 != title_dt_2b:
		print("Read_CUSTEEL錯誤:\n兩報價抓取的抬頭日期不相同，報價資料不齊全，結束抓取.\n")
		file.write("Read_CUSTEEL錯誤:\n兩報價抓取的抬頭日期不相同，報價資料不齊全，結束抓取.\n")
		return 1

	#合併df_no1與df_2b
	df_all = df_no1.merge(df_2b,on='dt')
	#print(df_all)

	#寫入/更新資料庫
	for i in range(0,len(df_all)):
		dt = df_all['dt'][i]

		# 最後維護日期時間
		str_date = str(datetime.datetime.now())
		date_last_maint = parser.parse(str_date).strftime("%Y%m%d")
		time_last_maint = parser.parse(str_date).strftime("%H%M%S")
		user_last_maint = "YUSTA00"

		#檢查資料是否已存在
		strsql  = "select count(*) from MARKET_304 "
		strsql += "where MARKET_DATE = '" + dt + "' "

		cursor = conn.execute(strsql)
		result = cursor.fetchone()

		if result[0] == 0:
			strsql  = "insert into MARKET_304 "
			strsql += "(MARKET_DATE,CUSTEEL_304_NO1_TK,CUSTEEL_304_NO1_BAO, "
			strsql += "CUSTEEL_304_NO1_LZ,CUSTEEL_304_2B_TK, "
			strsql += "CUSTEEL_304_2B_BXINGS,CUSTEEL_304_2B_LZ, "
			strsql += "DATE_LAST_MAINT,TIME_LAST_MAINT,USER_LAST_MAINT "
			strsql += ") values ("
			strsql += "'" + dt + "',"
			strsql += str(df_all['tk_price_no1'][i]) + ","
			strsql += str(df_all['bao_price_no1'][i]) + ","
			strsql += str(df_all['lz_price_no1'][i]) + ","
			strsql += str(df_all['tk_price_2b'][i]) + ","
			strsql += str(df_all['bx_price_2b'][i]) + ","
			strsql += str(df_all['lz_price_2b'][i]) + ","
			strsql += "'" + date_last_maint + "',"
			strsql += "'" + time_last_maint + "',"
			strsql += "'" + user_last_maint + "' "
			strsql += ")"
		else:
			strsql  = "update MARKET_304 set "
			strsql += "CUSTEEL_304_NO1_TK=" + str(df_all['tk_price_no1'][i]) + ", "
			strsql += "CUSTEEL_304_NO1_BAO=" + str(df_all['bao_price_no1'][i]) + ", "
			strsql += "CUSTEEL_304_NO1_LZ=" + str(df_all['lz_price_no1'][i]) + ", "
			strsql += "CUSTEEL_304_2B_TK=" + str(df_all['tk_price_2b'][i]) + ", "
			strsql += "CUSTEEL_304_2B_BXINGS=" + str(df_all['bx_price_2b'][i]) + ", "
			strsql += "CUSTEEL_304_2B_LZ=" + str(df_all['lz_price_2b'][i]) + ", "
			strsql += "DATE_LAST_MAINT='" + date_last_maint + "',"
			strsql += "TIME_LAST_MAINT='" + time_last_maint + "',"
			strsql += "USER_LAST_MAINT='" + user_last_maint + "' "
			strsql += "where MARKET_DATE='" + dt + "' "

		#print(strsql)

		try:
			conn.execute(strsql)

		except sqlite3.Error as er:
			err_flag = True
			file.write("Read_CUSTEEL資料庫錯誤:\n")
			file.write(strsql + "\n")
			file.write(er.args[0] + "\n")

			print("Read_CUSTEEL資料庫錯誤:\n")
			print(strsql + "\n")
			print("er=" + er.args[0] + "\n")

	if err_flag == False:
		file.write("Read_CUSTEEL資料庫insert/update成功.\n")
		print("Read_CUSTEEL資料庫insert/update成功.\n")
		conn.commit()
		return 0
	else:
		conn.execute("rollback")
		return 1

	#time.sleep(60)

	# 關閉瀏覽器視窗
	driver.quit();

def Read_MTP():
	toady = datetime.datetime.now()
	yyyy = str(toady.year)
	err_flag = False

	s = requests.session()

	#登入網站
	login_mtp = LoginWebSite.Login_MTP(s)

	if login_mtp == False:
		#登入失敗直接結束程式
		file.write("Read_MTP:\n登入metalprices.com網站失敗.\n")
		print("Read_MTP:\n登入metalprices.com網站失敗.\n")
		return 1

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
			data.append((row[0],row[1]))

	#print(data)
	df = pd.DataFrame(data, columns = ['dt','cash'])
	df = df.head(2)

	for i in range(0,len(df)):
		#print(str(df.index[i]))
		dt = str(df.iloc[i][0]) + " " + yyyy
		dt = parser.parse(dt).strftime("%Y%m%d")
		cash = str(df.iloc[i][1]).replace(",", "")
		print(dt + "  " + cash + "\n")

		# 最後維護日期時間
		str_date = str(datetime.datetime.now())
		date_last_maint = parser.parse(str_date).strftime("%Y%m%d")
		time_last_maint = parser.parse(str_date).strftime("%H%M%S")
		user_last_maint = "YUSTA00"

		#檢查資料是否已存在
		strsql  = "select count(*) from MARKET_304 "
		strsql += "where MARKET_DATE = '" + dt + "' "

		cursor = conn.execute(strsql)
		result = cursor.fetchone()

		if result[0] == 0:
			strsql  = "insert into MARKET_304 "
			strsql += "(MARKET_DATE,LME_NI,DATE_LAST_MAINT,TIME_LAST_MAINT,"
			strsql += "USER_LAST_MAINT"
			strsql += ") values ("
			strsql += "'" + dt + "',"
			strsql += cash + ","
			strsql += "'" + date_last_maint + "',"
			strsql += "'" + time_last_maint + "',"
			strsql += "'" + user_last_maint + "' "
			strsql += ")"
		else:
			strsql  = "update MARKET_304 set "
			strsql += "LME_NI=" + cash + ", "
			strsql += "DATE_LAST_MAINT='" + date_last_maint + "',"
			strsql += "TIME_LAST_MAINT='" + time_last_maint + "',"
			strsql += "USER_LAST_MAINT='" + user_last_maint + "' "
			strsql += "where MARKET_DATE='" + dt + "' "

		#print(strsql)

		try:
			conn.execute(strsql)

		except sqlite3.Error as er:
			err_flag = True
			file.write("Read_MTP資料庫錯誤:\n")
			file.write(strsql + "\n")
			file.write(er.args[0] + "\n")

			print("Read_MTP資料庫錯誤:\n")
			print(strsql + "\n")
			print("er=" + er.args[0] + "\n")

	if err_flag == False:
		file.write("Read_MTP資料庫insert/update成功.\n")
		print("Read_MTP資料庫insert/update成功.\n")
		conn.commit()
		return 0
	else:
		conn.execute("rollback")
		return 1

def Read_51BXG():
	#起訖日期(當天日期到往前推10天)
	str_date = str(datetime.datetime.now())
	str_date = parser.parse(str_date).strftime("%Y-%m-%d")
	end_date = str_date

	date_1 = datetime.datetime.strptime(end_date, "%Y-%m-%d")
	start_date = date_1 + datetime.timedelta(days=-10)
	start_date = str(start_date)[0:10]
	start_date = parser.parse(start_date).strftime("%Y-%m-%d")
	#print(start_date + "~" + end_date)

	err_flag = False

	s = requests.session()
	headers = {'User-Agent':'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'}

	#登入網站
	login_51bxg = LoginWebSite.Login_51BXG(s)

	if login_51bxg == False:
		#登入失敗直接結束程式
		file.write("Read_51BXG:\n登入 51bxg 網站失敗.\n")
		print("Read_51BXG:\n登入 51bxg 網站失敗.\n")
		return 1

	#讀取網頁資料(304 No.1)
	all_no1 = []
	for x in range(0,3):
		if x == 0:
			comp = '太钢不锈'
		elif x == 1:
			comp = '宝钢不锈'
		elif x == 2:
			comp = '鞍钢联众'

		URL  = 'http://www.51bxg.com/web/data_center/coil_price_list.aspx?'
		URL += 'type=卷&mkt=佛山市场&'
		URL += 'start_date=' + start_date + '&end_date=' + end_date + '&'
		URL += 'mat=304&'
		URL += 'transactionstatus=毛边&'
		URL += 'surf=No.1&'
		URL += 'fac=' + comp + '&'
		URL += 'width=1500&'
		URL += 'thick=4.0'

		#print(URL)

		r = s.get(URL, headers=headers)
		r.encoding = "utf-8"
		sp = BeautifulSoup(r.text, 'html.parser')

		table = sp.findAll('table', attrs={'class':'dc_data_list'})

		rdata = [[td.text for td in row.select('td')]
				 for row in table[0].select('tr')]
		#print(rdata)

		#排除空的list元素，與讀取需要的部分欄位
		data = []
		for row in rdata:
			if len(row) > 0:
				dt = str(row[8])[:10].replace("-","")		# 資料日期
				price = int(row[7].replace(" (含税)", ""))	# 毛邊價
				price_diff = int(row[5].replace("切边+", ""))	# 毛切邊差價
				price_cut = price + price_diff	# 切邊價
				data.append((dt, price, price_cut))

		#print(data)
		all_no1.append(data)

		#停頓隨機秒數
		random_sec = randint(1,3)
		time.sleep(random_sec)

	df1 = pd.DataFrame(all_no1[0], columns = ['dt','tk_price_no1','tk_price_cut_no1'])
	df2 = pd.DataFrame(all_no1[1], columns = ['dt','bao_price_no1','bao_price_cut_no1'])
	df3 = pd.DataFrame(all_no1[2], columns = ['dt','lz_price_no1','lz_price_cut_no1'])
	df_all_no1 = df1.merge(df2,on='dt').merge(df3,on='dt')
	df_all_no1['dl_304_no1'] = df_all_no1['lz_price_no1'] - 900
	#print(all_no1)
	#print(df_all_no1)

	#讀取網頁資料(304 2B)
	all_2b = []
	for x in range(0,2):
		if x == 0:
			comp = '张家港浦项'
			edge_type = '切边'
		elif x == 1:
			comp = '鞍钢联众'
			edge_type = '毛边'

		URL  = 'http://www.51bxg.com/web/data_center/coil_price_list.aspx?'
		URL += 'type=卷&mkt=佛山市场&'
		URL += 'start_date=' + start_date + '&end_date=' + end_date + '&'
		URL += 'mat=304&'
		URL += 'transactionstatus=' + edge_type + '&'
		URL += 'surf=2B&'
		URL += 'fac=' + comp + '&'
		URL += 'width=1219&'
		URL += 'thick=2.0'

		#print(URL)

		r = s.get(URL, headers=headers)
		r.encoding = "utf-8"
		sp = BeautifulSoup(r.text, 'html.parser')

		table = sp.findAll('table', attrs={'class':'dc_data_list'})

		rdata = [[td.text for td in row.select('td')]
				 for row in table[0].select('tr')]
		#print(rdata)

		#排除空的list元素，與讀取需要的部分欄位
		data = []
		for row in rdata:
			if len(row) > 0:
				if x == 0:	# 张家港浦项
					dt = str(row[8])[:10].replace("-","")		# 資料日期
					price_cut = int(row[7].replace(" (含税)", ""))	# 切邊價
					price_diff = int(row[5].replace("毛边-", ""))	# 毛切邊差價
					price = price_cut - price_diff	# 毛邊價
					data.append((dt, price, price_cut))
				elif x == 1: # 鞍钢联众
					dt = str(row[8])[:10].replace("-","")		# 資料日期
					price = int(row[7].replace(" (含税)", ""))		# 毛邊價
					price_diff = int(row[5].replace("切边+", ""))	# 毛切邊差價
					price_cut = price + price_diff	# 切邊價
					data.append((dt, price, price_cut))

		#print(data)
		all_2b.append(data)

		#停頓隨機秒數
		random_sec = randint(1,3)
		time.sleep(random_sec)

	df1 = pd.DataFrame(all_2b[0], columns = ['dt','zp_price_2b','zp_price_cut_2b'])
	df2 = pd.DataFrame(all_2b[1], columns = ['dt','lz_price_2b','lz_price_cut_2b'])
	df_all_2b = df1.merge(df2,on='dt')
	df_all_2b['dl_304_2b'] = df_all_2b['lz_price_2b'] - 1600
	#print(all_2b)
	#print(df_all_2b)

	#合併No.1與2B Dataframe
	df_all = df_all_no1.merge(df_all_2b,on='dt')
	#print(df_all)

	#寫入/更新資料庫
	for i in range(0,len(df_all)):
		dt = df_all['dt'][i]

		# 最後維護日期時間
		str_date = str(datetime.datetime.now())
		date_last_maint = parser.parse(str_date).strftime("%Y%m%d")
		time_last_maint = parser.parse(str_date).strftime("%H%M%S")
		user_last_maint = "YUSTA00"

		#檢查資料是否已存在
		strsql  = "select count(*) from MARKET_304 "
		strsql += "where MARKET_DATE = '" + dt + "' "

		cursor = conn.execute(strsql)
		result = cursor.fetchone()

		if result[0] == 0:
			strsql  = "insert into MARKET_304 "
			strsql += "(MARKET_DATE,DL_NO1_900_304,DL_2B_1600_304,TK_51_304_NO1, "
			strsql += "BAO_51_304_NO1,LZ_51_304_NO1, "
			strsql += "ZP_51_304_2B,LZ_51_304_2B, "
			strsql += "DATE_LAST_MAINT,TIME_LAST_MAINT,USER_LAST_MAINT "
			strsql += ") values ("
			strsql += "'" + dt + "',"
			strsql += str(df_all['dl_304_no1'][i]) + ","
			strsql += str(df_all['dl_304_2b'][i]) + ","
			strsql += str(df_all['tk_price_no1'][i]) + ","
			strsql += str(df_all['bao_price_no1'][i]) + ","
			strsql += str(df_all['lz_price_no1'][i]) + ","
			strsql += str(df_all['zp_price_2b'][i]) + ","
			strsql += str(df_all['lz_price_2b'][i]) + ","
			strsql += "'" + date_last_maint + "',"
			strsql += "'" + time_last_maint + "',"
			strsql += "'" + user_last_maint + "' "
			strsql += ")"
		else:
			strsql  = "update MARKET_304 set "
			strsql += "DL_NO1_900_304=" + str(df_all['dl_304_no1'][i]) + ", "
			strsql += "DL_2B_1600_304=" + str(df_all['dl_304_2b'][i]) + ", "
			strsql += "TK_51_304_NO1=" + str(df_all['tk_price_no1'][i]) + ", "
			strsql += "BAO_51_304_NO1=" + str(df_all['bao_price_no1'][i]) + ", "
			strsql += "LZ_51_304_NO1=" + str(df_all['lz_price_no1'][i]) + ", "
			strsql += "ZP_51_304_2B=" + str(df_all['zp_price_2b'][i]) + ", "
			strsql += "LZ_51_304_2B=" + str(df_all['lz_price_2b'][i]) + ", "
			strsql += "DATE_LAST_MAINT='" + date_last_maint + "',"
			strsql += "TIME_LAST_MAINT='" + time_last_maint + "',"
			strsql += "USER_LAST_MAINT='" + user_last_maint + "' "
			strsql += "where MARKET_DATE='" + dt + "' "

		#print(strsql)

		try:
			conn.execute(strsql)

		except sqlite3.Error as er:
			err_flag = True
			file.write("Read_51BXG資料庫錯誤:\n")
			file.write(strsql + "\n")
			file.write(er.args[0] + "\n")

			print("Read_51BXG資料庫錯誤:\n")
			print(strsql + "\n")
			print("er=" + er.args[0] + "\n")

	if err_flag == False:
		file.write("Read_51BXG資料庫insert/update成功.\n")
		print("Read_51BXG資料庫insert/update成功.\n")
		conn.commit()
		return 0
	else:
		conn.execute("rollback")
		return 1


def Read_CNCCM():
	err_flag = False

	s = requests.session()
	headers = {'User-Agent':'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'}

	#登入網站
	login_cnccm = LoginWebSite.Login_CNCCM(s)

	if login_cnccm == False:
		#登入失敗直接結束程式
		file.write("Read_CNCCM:\n登入 中華商務網 網站失敗.\n")
		print("Read_CNCCM:\n登入 中華商務網 網站失敗.\n")
		return 1

	#讀取網頁資料(304 2B)
	all_2b = []
	for x in range(0,4):
		if x == 0:
			comp = '太钢'
		elif x == 1:
			comp = '宝新'
		elif x == 2:
			comp = '张浦'
		elif x == 3:
			comp = '联众'

		URL  = 'http://www.chinaccm.com/PriceData/PriceData.aspx?'
		URL += 'Type=DATA_NATIONALPRICE%2c国内价格&Cata=1&scode=26&'
		URL += 'limit=MarketName%2c佛山%3bSpec%2c2.0*1219mm%3b'
		URL += 'Material%2c304%2f2B%3b'
		URL += 'ManuName%2c' + comp + '%3b&'
		URL += 'cdtion=&dshow=Date%2cSuppName%2cAreaName%2cProvinceName%2c'
		URL += 'MarketName%2cSpec%2cMaterial%2cPrice%2cPriceXXChange%2c'
		URL += 'PriceType%2cSpecTypeName%2cLocalityName%2cManuName%2cMarks'

		#print(URL)

		r = s.get(URL, headers=headers)
		r.encoding = "utf-8"
		sp = BeautifulSoup(r.text, 'html.parser')

		table = sp.findAll('table', attrs={'id':'GridView1'})

		rdata = [[td.text for td in row.select('td')]
				 for row in table[0].select('tr')]
		#print(rdata)

		#排除空的list元素，與讀取需要的部分欄位
		data = []
		for row in rdata:
			if len(row) > 0:
				dt = row[0].replace("-","")		# 資料日期
				price_cut = int(row[7])			# 切邊價
				price_diff = 200				# 毛切邊差價
				price = price_cut - price_diff	# 毛邊價
				data.append((dt, price, price_cut))

		#print(data)
		all_2b.append(data)

		#停頓隨機秒數
		random_sec = randint(1,3)
		time.sleep(random_sec)

	df1 = pd.DataFrame(all_2b[0], columns = ['dt','tk_price_2b','tk_price_cut_2b'])
	df2 = pd.DataFrame(all_2b[1], columns = ['dt','bx_price_2b','bx_price_cut_2b'])
	df3 = pd.DataFrame(all_2b[2], columns = ['dt','zp_price_2b','zp_price_cut_2b'])
	df4 = pd.DataFrame(all_2b[3], columns = ['dt','lz_price_2b','lz_price_cut_2b'])
	df_all_2b = df1.merge(df2,on='dt').merge(df3,on='dt').merge(df4,on='dt')
	#print(all_2b)
	#print(df_all_2b)

	#寫入/更新資料庫
	for i in range(0,len(df_all_2b)):
		dt = df_all_2b['dt'][i]

		# 最後維護日期時間
		str_date = str(datetime.datetime.now())
		date_last_maint = parser.parse(str_date).strftime("%Y%m%d")
		time_last_maint = parser.parse(str_date).strftime("%H%M%S")
		user_last_maint = "YUSTA00"

		#檢查資料是否已存在
		strsql  = "select count(*) from MARKET_304 "
		strsql += "where MARKET_DATE = '" + dt + "' "

		cursor = conn.execute(strsql)
		result = cursor.fetchone()

		if result[0] == 0:
			strsql  = "insert into MARKET_304 "
			strsql += "(MARKET_DATE,CHINACCM_304_2B_TK,CHINACCM_304_2B_BXINGS, "
			strsql += "CHINACCM_304_2B_ZP,CHINACCM_304_2B_LZ, "
			strsql += "DATE_LAST_MAINT,TIME_LAST_MAINT,USER_LAST_MAINT "
			strsql += ") values ("
			strsql += "'" + dt + "',"
			strsql += str(df_all_2b['tk_price_2b'][i]) + ","
			strsql += str(df_all_2b['bx_price_2b'][i]) + ","
			strsql += str(df_all_2b['zp_price_2b'][i]) + ","
			strsql += str(df_all_2b['lz_price_2b'][i]) + ","
			strsql += "'" + date_last_maint + "',"
			strsql += "'" + time_last_maint + "',"
			strsql += "'" + user_last_maint + "' "
			strsql += ")"
		else:
			strsql  = "update MARKET_304 set "
			strsql += "CHINACCM_304_2B_TK=" + str(df_all_2b['tk_price_2b'][i]) + ", "
			strsql += "CHINACCM_304_2B_BXINGS=" + str(df_all_2b['bx_price_2b'][i]) + ", "
			strsql += "CHINACCM_304_2B_ZP=" + str(df_all_2b['zp_price_2b'][i]) + ", "
			strsql += "CHINACCM_304_2B_LZ=" + str(df_all_2b['lz_price_2b'][i]) + ", "
			strsql += "DATE_LAST_MAINT='" + date_last_maint + "',"
			strsql += "TIME_LAST_MAINT='" + time_last_maint + "',"
			strsql += "USER_LAST_MAINT='" + user_last_maint + "' "
			strsql += "where MARKET_DATE='" + dt + "' "

		#print(strsql)

		try:
			conn.execute(strsql)

		except sqlite3.Error as er:
			err_flag = True
			file.write("Read_CNCCM資料庫錯誤:\n")
			file.write(strsql + "\n")
			file.write(er.args[0] + "\n")

			print("Read_CNCCM資料庫錯誤:\n")
			print(strsql + "\n")
			print("er=" + er.args[0] + "\n")

	if err_flag == False:
		file.write("Read_CNCCM資料庫insert/update成功.\n")
		print("Read_CNCCM資料庫insert/update成功.\n")
		conn.commit()
		return 0
	else:
		conn.execute("rollback")
		return 1


############################################################################
# Main                                                                     #
############################################################################
print("Executing cn_mkt_304_info...")

#寫入LOG File
dt=datetime.datetime.now()
str_date = str(dt)
str_date = parser.parse(str_date).strftime("%Y%m%d")

name = "cn_mkt_304_info_" + str_date + ".txt"
file = open(name, 'a', encoding = 'UTF-8')

tStart = time.time()#計時開始
file.write("\n\n\n*** LOG datetime  " + str(datetime.datetime.now()) + " ***\n")

#建立資料庫連線
conn = sqlite3.connect("yusco.db")

print("Read metalprices.com ...")
rt1 = Read_MTP()
#print(rt1)

print("Read 51bxg ...")
rt2 = Read_51BXG()
#print(rt2)

print("Read cnccm ...")
rt3 = Read_CNCCM()
#print(rt3)

print("Read custeel ...")
rt4 = Read_CUSTEEL()
#print(rt4)

tEnd = time.time()#計時結束
file.write ("\n\n\n結轉耗時 %f sec\n" % (tEnd - tStart)) #會自動做進位
file.write("*** End LOG ***\n\n")

# Close File
file.close()

#關閉資料庫連線
conn.close

"""
# 如果執行過程無錯誤，最後刪除log file
err_cnt = rt1 + rt2 + rt3 + rt4
if err_cnt == 0:
    os.remove(name)
"""
print("End of prog...")