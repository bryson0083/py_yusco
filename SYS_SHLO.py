import os
import sys
import telnetlib
import time
import json
import datetime
import pandas as pd
import sqlite3
import sqlalchemy
from ftplib import FTP
from datetime import date
from contextlib import suppress
from dateutil import parser

### 以下import自行開發公用程式 ###
import util.GET_LOGIN_ID as GET_LO_ID
import util.FTP_SHLO_LOG as FTP_LOG

def DEL_36A_SHLO_LOG():
	global log_file

	print("刪除CPS 36A上的SHOW LOCK LOG檔案...")
	str_dt = str(datetime.datetime.now())
	str_dt = parser.parse(str_dt).strftime("%Y%m%d%H%M%S")

	timeout = 20
	USER_ID, PASSWORD = GET_LO_ID.GET_LOGIN_ID('axp36a_cps')

	host_ip = '100.1.1.6'

	try:
		tn = telnetlib.Telnet(host_ip) 
	except Exception as e:
		f = open('SYS_SHLO_LOG.TXT', 'a')
		f.write('Err on SYS_SHLO create a telnet link(' + host_ip +').\n')
		f.write('funtion: DEL_36A_SHLO_LOG\n')
		f.write('time:' + str_dt + '\n')
		f.write(str(e.args))
		f.write('\n\n')
		f.close()
		return

	#for debug
	#tn.set_debuglevel(1)

	tn.read_until(b"Username: ",timeout)
	tn.write(USER_ID.encode('ascii') + b"\r")

	tn.read_until(b"Password: ",timeout)
	tn.write(PASSWORD.encode('ascii') + b"\r")

	#waiting for prompt
	tn.read_until(b"[MIS.CPS]",timeout)
	tn.write(b'\r')

	log_file = "SHLO_60E.TXT"
	str_cmd = "DEL " + log_file + ";* /NOCON\r"
	print(str_cmd)
	tn.read_until(b"[MIS.CPS]",timeout)
	tn.write(str_cmd.encode())	# string convert to bytes format

	log_file = "SHLO_76A.TXT"
	str_cmd = "DEL " + log_file + ";* /NOCON\r"
	print(str_cmd)
	tn.read_until(b"[MIS.CPS]",timeout)
	tn.write(str_cmd.encode())	# string convert to bytes format

	tn.read_until(b"[MIS.CPS]",timeout)
	tn.write(b"logout\r")
	time.sleep(1)

	#close connection
	tn.close()
	print("刪除36A SHOW LOCK LOG檔案，完畢...\n\n\n")

def SYS_SHLO(arg_host):
	global log_file

	print("執行" + arg_host + "系統LOCK檢查作業...\n")

	str_dt = str(datetime.datetime.now())
	str_dt = parser.parse(str_dt).strftime("%Y%m%d%H%M%S")

	if arg_host == "AXP76A":
		host_ip = '100.1.1.2'
		log_file = 'SHLO_76A.TXT'
	else:
		host_ip = '100.1.1.3'
		log_file = 'SHLO_60E.TXT'

	timeout = 20
	log_timeout = 180

	try:
		tn = telnetlib.Telnet(host_ip) 
	except Exception as e:
		f = open('SYS_SHLO_LOG.TXT', 'a')
		f.write('Err on SYS_SHLO create a telnet link(' + host_ip +').\n')
		f.write('funtion: SYS_SHLO\n')
		f.write('time:' + str_dt + '\n')
		f.write(str(e.args))
		f.write('\n\n')
		f.close()
		return

	#for debug
	#tn.set_debuglevel(1)

	USER_ID, PASSWORD = GET_LO_ID.GET_LOGIN_ID('axp76a_mgr')

	tn.read_until(b"Username: ",timeout)
	tn.write(USER_ID.encode('ascii') + b"\r")

	tn.read_until(b"Password: ",timeout)
	tn.write(PASSWORD.encode('ascii') + b"\r")

	#waiting for prompt
	tn.read_until(b"[MIS.MGR]",timeout)
	tn.write(b'\r')

	str_cmd = "DEL " + log_file + ";* /NOCON\r"
	print(str_cmd)
	tn.read_until(b"[MIS.MGR]",timeout)
	tn.write(str_cmd.encode())	# string convert to bytes format

	str_cmd = "SHLO /OUT=" + log_file + "\r"
	print(str_cmd)
	tn.read_until(b"[MIS.MGR]",timeout)
	tn.write(str_cmd.encode())	# string convert to bytes format

	cps36a_id, cps36a_pwd = GET_LO_ID.GET_LOGIN_ID('axp36a_cps')

	str_cmd = 'copy ' + log_file + ' axp36a"' + cps36a_id + ' ' + cps36a_pwd + '"::sys$login:*.* \r'
	#print(str_cmd)
	tn.read_until(b"[MIS.MGR]",log_timeout)
	tn.write(str_cmd.encode())	# string convert to bytes format

	tn.read_until(b"[MIS.MGR]",timeout)
	tn.write(b"logout\r")
	time.sleep(1)

	#close connection
	tn.close()
	print(arg_host + "系統LOCK檢查作業結束，等待下次執行...\n\n\n")


def FILE_IS_EXIST(arg_file_name):
	#判斷LOG檔案是否存在
	is_existed = os.path.exists(arg_file_name)
	if is_existed == False:
		#print(arg_file_name + " 無此檔.\n")
		return False
	else:
		return True

def COLLECT_LOG():

	ls_file = []
	if FILE_IS_EXIST('SHLO_60E.TXT'):
		ls_file.append('SHLO_60E.TXT')

	if FILE_IS_EXIST('SHLO_76A.TXT'):
		ls_file.append('SHLO_76A.TXT')

	for log_file in ls_file:
		#log_file = 'SHLO_60E.TXT'
		f = open(log_file, 'r')
		lst = f.readlines()
		#print(lst)

		str_dt = str(datetime.datetime.now())
		str_dt = parser.parse(str_dt).strftime("%Y%m%d%H%M%S")

		del_flag = False
		for x in lst:
			if x.find('no locks on this node with the specified qualifiers') > 0:
				del_flag = True
				print(x)

		f.close()
		print("Final del_flag ==>" + str(del_flag))

		if del_flag == False:
			print("檢視 LOG FILE =>" + log_file + "，有系統LOCK訊息，留存LOG FILE.")

			new_log_file = log_file + "." + str_dt + ".txt"
			cwd = os.getcwd()
			tar_file = cwd + "\\" + log_file
			des_file = cwd + "\\shlo_log\\" + new_log_file

			try:
				os.rename(tar_file, des_file)
				print(log_file + "移動檔案完畢.")
			except Exception as e:
				print(log_file + "移動檔案失敗.")
				print(e.args)
		else:
			print("檢視 LOG FILE =>" + log_file + "，無系統LOCK訊息，刪除LOG FILE.")
			os.remove(log_file)

def COLLECT_LOG2():
	ls_file = []
	if FILE_IS_EXIST('SHLO_60E.TXT'):
		ls_file.append('SHLO_60E.TXT')

	if FILE_IS_EXIST('SHLO_76A.TXT'):
		ls_file.append('SHLO_76A.TXT')

	del_cnt = 0
	for log_file in ls_file:
		f = open(log_file, 'r')
		lst = f.readlines()

		for x in lst:
			if x.find('no locks on this node with the specified qualifiers') > 0:
				del_cnt += 1
				print(x)

		f.close()
		print("Final del_cnt ==>" + str(del_cnt))

	if del_cnt < 2:
		print("目前系統有LOCK狀況，合併產生新LOG FILE.")
		str_dt = str(datetime.datetime.now())
		str_dt = parser.parse(str_dt).strftime("%Y%m%d%H%M%S")

		log_fname = 'shlo_log/SHLO_LOG_' + str_dt + '.txt'
		with open(log_fname, 'w') as outfile:
			for log_file in ls_file:
				with open(log_file) as infile:
					outfile.write('lock information from ' + log_file + '\n\n')
					outfile.write(infile.read())
		print("合併LOG FILE完畢.")
		JLOCK(log_fname)

	else:
		print("目前無任何系統LOCK訊息.")

	#下載回來的舊LOG刪除
	for log_file in ls_file:
		os.remove(log_file)

def JLOCK(log_fname):
	print("進行Process判斷，並建議可排除process...")
	pd.options.mode.chained_assignment = None

	f = open(log_fname, 'r')
	lst = f.readlines()

	info_ls = []
	wt = 0
	for x in lst:
		ls_tmp = x.split(' ')
		ls_msg = []
		for msg in ls_tmp:
			ls_msg.append(msg.strip())

		ls_msg = list(filter(None, ls_msg))
		#print(ls_msg)

		#lk_host = ''
		if (x.find('SHLO_76A.TXT') >= 0):
			lk_host = 'AXP76A'

		if (x.find('SHLO_60E.TXT') >= 0):
			lk_host = 'AXP60E'

		if ((x.find('Blocker:') >= 0) or 
		    (x.find('Waiting:') >= 0)):

			if (x.find('Waiting:') >= 0):
				wt = 1
			else:
				wt += 1

			ls_msg[0] = ls_msg[0].strip(':')
			ls_msg[3] = lk_host
			ls_msg[4] = wt
			info_ls.append(ls_msg[0:5])
			#print(ls_msg)

	#關閉檔案
	f.close()

	#list資料讀入dataframe
	df = pd.DataFrame(info_ls, columns=['TYPE', 'PID', 'PNAME', 'HOST', 'WT'])
	df['SWEEP'] = 'N'
	df['LK_ID'] = ' '
	idx = 1
	for i in range(0,len(df)):
		tp = df['TYPE'][i]
		#print(tp)

		if i > 0 and tp == "Waiting":
			idx += 1
			df['SWEEP'][i-1] = 'Y'

		df['LK_ID'][i] = 'LK' + str(idx).zfill(3)

	df['SWEEP'].iloc[-1] = 'Y'

	# 建立資料庫連線
	conn = sqlite3.connect('yusco.db')
	engine = sqlalchemy.create_engine('sqlite:///yusco.db')

	#清空table
	sqlstr  = "delete from SHLO"
	conn.execute(sqlstr)
	conn.commit()

	#dataframe資料寫入資料庫
	df.to_sql('SHLO', conn, if_exists='replace')

	#篩選出初步列為可排除process
	df2 = df.loc[df['SWEEP'] == 'Y']
	df2 = df2.loc[:,['PID','PNAME']]
	df2 = df2.drop_duplicates()
	#print(df2.drop_duplicates())
	#print(df2.drop_duplicates().values.tolist())
	df2 = df2.reset_index(drop=True)

	print("初步可排除process")
	print(df2)

	cursor = conn.cursor()
	for i in range(0,len(df2)):
		proc = df2['PID'][i]
		upd_flag = False

		#排除一開始被列為可排除，但本身也是被其他process擋住
		sqlstr = "select LK_ID, WT from SHLO where PID='" + proc + "'"
		cursor.execute(sqlstr)
		result = cursor.fetchall()

		if len(result) > 0:
			lk_id_tp = result

			for elem in lk_id_tp:
				lk_id = elem[0]
				proc_wt = int(elem[1])
			
				sqlstr = "select MAX(WT) from SHLO where LK_ID='" + lk_id + "' and PID !='" + proc + "' "
				cursor.execute(sqlstr)
				rt = cursor.fetchone()

				max_wt = 0
				if len(rt) > 0:
					max_wt = int(rt[0])

				if max_wt > proc_wt:
					upd_flag = True

		if upd_flag == True:
			sqlstr = "update SHLO set SWEEP = 'N' where PID = '" + proc + "' "
			cursor.execute(sqlstr)
			conn.commit()

	df2 = pd.read_sql_query('select PID, PNAME from SHLO where SWEEP="Y"',con = engine)
	df2 = df2.drop_duplicates()

	with open(log_fname, 'a') as outfile:
		print('建議排除Process:')
		print(df2)
		outfile.write('\n\n\n建議排除Process:\n')
		outfile.write(df2.to_string())
		outfile.write('\n\n')

	#關閉資料庫連線
	conn.close
	engine.dispose()

	print("判斷建議可排除process完畢...")

def MAIN_SYS_SHLO():
	print('系統 LOCK 檢查開始...')
	str_dt = str(datetime.datetime.now())
	str_dt = parser.parse(str_dt).strftime("%Y%m%d%H%M%S")

	try:
		SYS_SHLO('AXP76A')
		SYS_SHLO('AXP60E')
		FTP_LOG.ftp_shlo_log()
		DEL_36A_SHLO_LOG()
		COLLECT_LOG2()

	except Exception as e:
		print('Err on MAIN_SYS_SHLO.')
		print(e.args)
		f = open('SYS_SHLO_LOG.TXT', 'a')
		f.write('Err on MAIN_SYS_SHLO.\n')
		f.write('time:' + str_dt + '\n')
		f.write(str(e.args))
		f.write('\n\n')
		f.close()
		return

	print('系統 LOCK 檢查結束...\n\n')

if __name__ == '__main__':
	MAIN_SYS_SHLO()