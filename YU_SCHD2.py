# -*- coding: utf-8 -*-
"""
定時排程管理 tmp (測試程式用)

@author: Bryson Xue

@Note: 
	不與正式排程程式一起執行

"""
import schedule
import time
import multiprocessing
import os.path
import datetime
from dateutil.parser import parse
from dateutil import parser

#以下為非公用程式import
import SYS_SHLO as SHLO
import QA_PHOTO_BAK as QA_BAK
import HSMW_PLAN_STAT as HSMW
import DAILY_MAIL_TEST as MAIL_SEND

def job():
	str_date = str(datetime.datetime.now())
	print("執行job 1: 目前時間:" + str_date + "\n")

	try:
		SHLO.MAIN_SYS_SHLO()
	except Exception as e:
		print('Err: YU_SCHD2 job 執行出現錯誤，等待下次執行...')
		print("SYS_SHLO Err:\n" + str_date + "\n" + str(e.args) + "\n\n")
		f = open("YU_SCHD2_LOG.txt", "a")
		f.write("SYS_SHLO Err:\n" + str_date + "\n" + str(e.args) + "\n\n")
		f.close()
		return

def job2():
	#取得目前時間
	dt = datetime.datetime.now()
	str_day = str(dt.day)	#取得當天日期，日的部分
	#print(str_day)

	str_date = str(dt)
	str_date = parser.parse(str_date).strftime("%Y%m%d")

	print("執行job 2: 目前時間:" + str_date + "\n")

	try:
		if str_day == "3":
			QA_BAK.MAIN_QA_PHOTO_BAK()
		else:
			print('每個月的第3日執行，未到執行日期，等待下次執行...')

	except Exception as e:
		print('Err: YU_SCHD2 job 執行出現錯誤，等待下次執行...')
		print("SYS_SHLO Err:\n" + str_date + "\n" + str(e.args) + "\n\n")
		f = open("YU_SCHD2_LOG.txt", "a")
		f.write("SYS_SHLO Err:\n" + str_date + "\n" + str(e.args) + "\n\n")
		f.close()
		return

def job3():
	str_date = str(datetime.datetime.now())
	print("執行job 3: 目前時間:" + str_date + "\n")

	try:
		HSMW.HSMW_PLAN_STAT()
	except Exception as e:
		print('Err: YU_SCHD2 job3 執行出現錯誤，等待下次執行...')
		print("HSMW Err:\n" + str_date + "\n" + str(e.args) + "\n\n")
		f = open("YU_SCHD2_LOG.txt", "a")
		f.write("HSMW Err:\n" + str_date + "\n" + str(e.args) + "\n\n")
		f.close()
		return

def job4():
	#取得目前時間
	dt = datetime.datetime.now()
	str_day = str(dt.day)	#取得當天日期，日的部分
	#print(str_day)

	str_date = str(dt)
	str_date = parser.parse(str_date).strftime("%Y%m%d")

	print("執行job 4: 目前時間:" + str_date + "\n")

	try:
		MAIL_SEND.MAIL_TEST()
	except Exception as e:
		print('Err: YU_SCHD2 job 4 執行出現錯誤，等待下次執行...')
		print("SYS_SHLO Err:\n" + str_date + "\n" + str(e.args) + "\n\n")
		f = open("YU_SCHD2_LOG.txt", "a")
		f.write("SYS_SHLO execute job4 Err:\n" + str_date + "\n" + str(e.args) + "\n\n")
		f.close()
		return


if __name__ == '__main__':
	#取得目前時間
	str_date = str(datetime.datetime.now())
	str_date = parser.parse(str_date).strftime("%Y%m%d")

	#手動測試單獨執行用
	#MAIL_SEND.MAIL_TEST()

	#SYS SHOW LOCK
	schedule.every(10).minutes.do(job)

	#QA_PHOTO備份(每個月的第3日執行)
	#schedule.every().day.at("10:00").do(job2)

	#熱軋生計排程SCH檢查
	schedule.every(10).minutes.do(job3)

	#DAILY MAIL 發送測試
	schedule.every().day.at("10:00").do(job4)

	while True:
	    schedule.run_pending()
	    time.sleep(1)