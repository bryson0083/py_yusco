import sys
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

print("Executing MTK304_CUSTEEL...")
#寫入LOG File
dt=datetime.datetime.now()
str_date = str(dt)
str_date = parser.parse(str_date).strftime("%Y%m%d")

name = "MTK304_CUSTEEL_" + str_date + ".txt"
file = open(name, 'a', encoding = 'UTF-8')

tStart = time.time()#計時開始
file.write("\n\n\n*** LOG datetime  " + str(datetime.datetime.now()) + " ***\n")

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
	#print("Read_CUSTEEL錯誤:\n兩報價抓取的抬頭日期不相同，報價資料不齊全，結束抓取.\n")
	file.write("Read_CUSTEEL錯誤:\n兩報價抓取的抬頭日期不相同，報價資料不齊全，結束抓取.\n")
	sys.exit("Read_CUSTEEL錯誤:\n兩報價抓取的抬頭日期不相同，報價資料不齊全，結束抓取.")

#合併df_no1與df_2b
df_all = df_no1.merge(df_2b,on='dt')
#print(df_all)

#建立資料庫連線
conn = sqlite3.connect("yusco.db")

err_flag = False

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
else:
	conn.execute("rollback")

#time.sleep(60)

# 關閉瀏覽器視窗
driver.quit();

tEnd = time.time()#計時結束
file.write ("\n\n\n結轉耗時 %f sec\n" % (tEnd - tStart)) #會自動做進位
file.write("*** End LOG ***\n\n")

# Close File
file.close()

#關閉資料庫連線
conn.close

# 如果執行過程無錯誤，最後刪除log file
if err_flag == False:
    os.remove(name)

print("End of prog...")