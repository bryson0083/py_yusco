# -*- coding: utf-8 -*-
"""
熱軋生計排程SCH狀態檢查

@author: Bryson Xue

@Note: 
	確認產線HSM是否運行中，並回傳代碼(1運轉, 0停機, 99:不明錯誤)

	若熱軋生計網頁因HPS SCH process異常，造成網頁資料一段時間後都沒更新的問題。
	透過程式定時檢查，若SCH LOG最新一筆紀錄日期時間與檢查當下時間差距太大
	(目前設定門檻為30分鐘)，則重啟HPS SCH process。
	若HSM產線狀況為停機狀態，則不做檢查。

	type SCH20180301.LOG /tail=10  

"""
import pyodbc 
import os
import sys
import telnetlib
import time
import datetime
from datetime import date
from dateutil import parser
from dateutil.relativedelta import relativedelta
import sqlite3

### 以下import自行開發公用程式 ###
import util.CHK_HSM_STAT as hsm_stat
import util.GET_LOGIN_ID as GET_LO_ID

def rd_hps_log():
	global file

	host_ip = '100.1.1.2'	#AXP76A
	str_dt = str(datetime.datetime.now())
	str_dt = parser.parse(str_dt).strftime("%Y%m%d")

	timeout = 20
	tot_diff_minu = 0

	try:
		tn = telnetlib.Telnet(host_ip) 
	except Exception as e:
		file.write('Err on rd_hps_log create a telnet link(' + host_ip +').\n')
		file.write('funtion: rd_hps_log\n')
		file.write('time:' + str_dt + '\n')
		file.write(str(e.args))
		file.write('\n\n')
		return 99

	#tn.set_debuglevel(1)

	USER_ID, PASSWORD = GET_LO_ID.GET_LOGIN_ID('axp76a_hps')

	tn.read_until(b"Username: ",timeout)
	tn.write(USER_ID.encode('ascii') + b"\r")

	tn.read_until(b"Password: ",timeout)
	tn.write(PASSWORD.encode('ascii') + b"\r")

	#waiting for prompt
	tn.read_until(b"[MIS.HPS.LOG]",timeout)
	tn.write(b'\r')

	str_cmd = "TYPE SCH" + str_dt + ".LOG /tail=10\r"
	#str_cmd = "TYPE SCH20180401.LOG /tail=10\r"

	print(str_cmd)
	tn.read_until(b"[MIS.HPS.LOG]",timeout)
	tn.write(str_cmd.encode())	# string convert to bytes format

	date_fmt = "%Y/%m/%d-%H:%M:%S"
	cnt = 0
	log_last_dt = ""
	while True:
		try:
			line = tn.read_until(b"\r",timeout)  # Check for new line and CR
			line_str = line.decode("ASCII")
			print(line_str)
		except Exception as e:
			line_str = ""
			print("The return string is decoding error.")
			print("The origin string =>" + str(line))
			print(str(e.args))
			file.write("The return string is decoding error.\n")
			file.write("The origin string =>" + str(line) + "\n")
			file.write(str(e.args))
			file.write('\n\n')

		if (b"[MIS.HPS.LOG]") in line:   # If last read line is the prompt, end loop
			break

		if len(line_str.strip()) > 16:
			log_last_dt = line_str[2:21]
			#print("Substring =>" + log_last_dt)

	str_dt = str(datetime.datetime.now())
	curr_dt = parser.parse(str_dt).strftime(date_fmt)
	print("log_last_dt='" + log_last_dt + "'")
	print("curr_dt='" + curr_dt + "'")
	file.write("log_last_dt='" + log_last_dt + "'\n")
	file.write("curr_dt='" + curr_dt + "'\n")

	try:
		a = datetime.datetime.strptime(log_last_dt, date_fmt)	#LOG紀錄最後日期時間
		b = datetime.datetime.strptime(curr_dt, date_fmt)		#系統目前日期時間
		delta = b - a

		tot_diff_minu = delta.days * 1440 + delta.seconds / 60	#時間差(分鐘)
		print("tot_diff_minu=" + str(tot_diff_minu))
		file.write("tot_diff_minu=" + str(tot_diff_minu) + "\n")

	except Exception as e:
		print("TYPE 指令異常，略過本次檢查...")
		file.write("TYPE 指令異常，略過本次檢查...\n")
		file.write('Err on rd_hps_log()\n')
		file.write('time:' + curr_dt + '\n')
		file.write(str(e.args))
		file.write('\n\n')
		return 99

	tn.read_until(b"[MIS.HPS.LOG]",timeout)
	tn.write(b"logout\r")
	time.sleep(1)

	#close connection
	tn.close()

	return tot_diff_minu

	print("rd_hps_log，完畢...\n\n\n")


def rest_hsm_sch():
	global file

	host_ip = '100.1.1.2'	#AXP76A
	str_dt = str(datetime.datetime.now())
	str_dt = parser.parse(str_dt).strftime("%Y%m%d")

	timeout = 20
	recnt = 0

	try:
		tn = telnetlib.Telnet(host_ip) 
	except Exception as e:
		file.write('Err on rest_hsm_sch create a telnet link(' + host_ip +').\n')
		file.write('funtion: rest_hsm_sch\n')
		file.write('time:' + str_dt + '\n')
		file.write(str(e.args))
		file.write('\n\n')
		return

	USER_ID, PASSWORD = GET_LO_ID.GET_LOGIN_ID('axp76a_hps')

	tn.read_until(b"Username: ",timeout)
	tn.write(USER_ID.encode('ascii') + b"\r")

	tn.read_until(b"Password: ",timeout)
	tn.write(PASSWORD.encode('ascii') + b"\r")

	#waiting for prompt
	tn.read_until(b"[MIS.HPS.LOG]",timeout)
	tn.write(b'\r')

	# 建立資料庫連線
	conn = sqlite3.connect('yusco.db')

	# 讀取當天重啟次數
	sqlstr = "select RECONNECT_CNT from HSMW_PLAN_STAT "
	sqlstr = sqlstr + "where "
	sqlstr = sqlstr + "CHK_DATE='" + str_dt + "' "

	#print(sqlstr)
	cursor = conn.execute(sqlstr)
	result = cursor.fetchone()

	if result is not None:
		recnt = result[0]
	else:
		sqlstr  = "insert into HSMW_PLAN_STAT (CHK_DATE, RECONNECT_CNT) values ("
		sqlstr += "'" + str_dt + "',0)"

		try:
			conn.execute(sqlstr)
			conn.commit()
		except sqlite3.Error as er:
			print("insert HSMW_PLAN_STAT RECONNECT_CNT er=" + er.args[0] + "\n")
			print(str_dt + " RECONNECT_CNT資料新增異常...Rollback!\n")
			file.write("insert HSMW_PLAN_STAT RECONNECT_CNT er=" + er.args[0] + "\n")
			file.write(str_dt + " RECONNECT_CNT資料新增異常...Rollback!\n")
			conn.execute("rollback")

	if recnt < 3:
		str_cmd = "STOP SCH\r"
		print(str_cmd)
		file.write(str_cmd + "\n")
		tn.read_until(b"[MIS.HPS.LOG]",timeout)
		tn.write(str_cmd.encode())	# string convert to bytes format

		time.sleep(5)

		str_cmd = "SV\r"
		print(str_cmd)
		file.write(str_cmd + "\n")
		tn.read_until(b"[MIS.HPS.LOG]",timeout)
		tn.write(str_cmd.encode())	# string convert to bytes format

		# 更新當天重啟次數
		recnt += 1
		sqlstr  = "update HSMW_PLAN_STAT set RECONNECT_CNT = " + str(recnt) + " "
		sqlstr += "where CHK_DATE='" + str_dt + "'"

		try:
			conn.execute(sqlstr)
			conn.commit()
		except sqlite3.Error as er:
			str_dt = str(datetime.datetime.now())
			print("update HSMW_PLAN_STAT RECONNECT_CNT er=" + er.args[0] + "\n")
			print(str_dt + " RECONNECT_CNT=" + str(recnt) + "資料更新異常...Rollback!\n")
			file.write("update HSMW_PLAN_STAT RECONNECT_CNT er=" + er.args[0] + "\n")
			file.write(str_dt + " RECONNECT_CNT=" + str(recnt) + "資料更新異常...Rollback!\n")
			conn.execute("rollback")
	else:
		print("$$$ 當天重啟次數已達三次，不再進行重啟. $$$\n")
		file.write("$$$ 當天重啟次數已達三次，不再進行重啟. $$$\n")

	tn.read_until(b"[MIS.HPS.LOG]",timeout)
	tn.write(b"logout\r")
	time.sleep(1)

	#close connection
	tn.close()

	# 資料庫連線關閉
	conn.close()	


def HSMW_PLAN_STAT():
	print("Executing " + os.path.basename(__file__) + "...")

	str_dt = str(datetime.datetime.now())
	str_dt = parser.parse(str_dt).strftime("%Y%m%d")

	#運行紀錄LOG
	global file
	name = "HSMW_PLAN_STAT_" + str_dt + ".txt"
	file = open(name, 'a', encoding = 'UTF-8')

	file.write("\n\n\n*** LOG datetime  " + str(datetime.datetime.now()) + " ***\n")
	file.write("執行HSMW 熱軋生計排程SCH檢查...\n\n")

	#HSM產線運作狀況
	hsm_stat_code = hsm_stat.CHK_HSM_STAT()
	#print(type(hsm_stat_code))
	#print(hsm_stat_code)

	if (hsm_stat_code == 0):
		print("目前產線狀況碼=" + str(hsm_stat_code) + " =>停機中，不做後續檢查.")
		file.write("目前產線狀況碼=" + str(hsm_stat_code) + " =>停機中，不做後續檢查.\n")
	elif (hsm_stat_code == 99):
		print("目前產線狀況碼=" + str(hsm_stat_code) + " =>檢查異常，略過後續檢查.")
		file.write("目前產線狀況碼=" + str(hsm_stat_code) + " =>檢查異常，略過後續檢查.\n")
	else:
		print("目前產線狀況碼=" + str(hsm_stat_code) + " =>運轉中，進行後續檢查...")
		file.write("目前產線狀況碼=" + str(hsm_stat_code) + " =>運轉中，進行後續檢查...\n")

		try:
			time_diff = rd_hps_log()

			if time_diff == 99:
				raise ValueError('讀取HPS LOG異常...', 'foo', 'bar', 'baz')

			#若差距時間大於30分鐘，重啟SCH
			if time_diff > 30:
				print("$$$ 差距時間大於30分鐘，重啟SCH... $$$")
				file.write("$$$ 差距時間大於30分鐘，重啟SCH... $$$\n")
				rest_hsm_sch()
			else:
				print("目前 熱軋生計SCH 狀況正常...")
				file.write("目前 熱軋生計SCH 狀況正常...\n")
		except Exception as e:
			print('Err: HPS SCH檢查出現未預期錯誤，等待下次執行...')
			print("HSMW_PLAN_STAT Err:\n" + str(datetime.datetime.now()) + "\n" + str(e.args[0]) + "\n\n")
			file.write('Err: HPS SCH檢查出現未預期錯誤，等待下次執行...\n')
			file.write("HSMW_PLAN_STAT Err:\n" + str(datetime.datetime.now()) + "\n" + str(e.args[0]) + "\n\n")
			file.close()
			return

	file.write("\n\n*** End LOG ***\n\n\n")

	# Close File
	file.close()

	print("本次HSMW 熱軋生計排程SCH檢查結束，等待下次執行...\n\n\n")	


if __name__ == '__main__':
	HSMW_PLAN_STAT()