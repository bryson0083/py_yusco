# -*- coding: utf-8 -*-
"""
定時排程管理

@author: Bryson Xue

@Note: 
	所有需要執行之排程程序，集中管理執行

@Ref:
	https://schedule.readthedocs.io/en/stable/

"""
import schedule
import time
import multiprocessing
import os.path
import datetime
from dateutil.parser import parse
from dateutil import parser

#以下為非公用程式import
import AP4_AGENT_V27 as ap4
import AP4_SEAR_1003_V1_3 as Err1003
import cn_mkt_304_info_v2_4_3 as mkt304
import CPS_DEL_LOG_V2 as cps_log_del
import CRM_DEL_LOG_V2 as crm_log_del

def job():
	str_date = str(datetime.datetime.now())
	print("執行job 1: 目前時間:" + str_date + "\n")
	ap4.MAIN_CHK_AP4()

def job2():
	str_date = str(datetime.datetime.now())
	print("執行job 2: 目前時間:" + str_date + "\n")
	Err1003.MAIN_CHK_Err1003()

def job3():
	str_date = str(datetime.datetime.now())
	print("執行job 3: 目前時間:" + str_date + "\n")
	mkt304.MAIN_CN_MKT_304()

def job4():
	str_date = str(datetime.datetime.now())
	print("執行job 4: 目前時間:" + str_date + "\n")
	cps_log_del.DEL_CPS_LOG()
	crm_log_del.DEL_CRM_LOG()

if __name__ == '__main__':
	#取得目前時間
	dt = datetime.datetime.now()
	str_day = str(dt.day)	#取得當天日期，日的部分
	#print(str_day)

	#手動測試單獨執行用
	#ap4.MAIN_CHK_AP4()
	#Err1003.MAIN_CHK_Err1003()
	#mkt304.MAIN_CN_MKT_304()
	#cps_log_del.DEL_CPS_LOG()
	#crm_log_del.DEL_CRM_LOG()

	#AP4傳輸檢查
	schedule.every(15).minutes.do(job)

	#AP4傳輸RDB-1003錯誤偵測
	schedule.every(10).minutes.do(job2)

	#市場資訊報價抓取
	schedule.every().day.at("12:50").do(job3)
	schedule.every().day.at("14:00").do(job3)

	#CPS、CRM舊LOG檔案刪除(每個月的第3日執行)
	if str_day == "3":
		schedule.every().day.at("09:10").do(job4)

	while True:
	    schedule.run_pending()
	    time.sleep(1)