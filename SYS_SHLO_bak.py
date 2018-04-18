import os
import sys
import telnetlib
import time
import json
import datetime
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
		f.write(e.args)
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
		f.write(e.args)
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

def MAIN_SYS_SHLO():
	print('系統 LOCK 檢查開始...')
	str_dt = str(datetime.datetime.now())
	str_dt = parser.parse(str_dt).strftime("%Y%m%d%H%M%S")

	try:
		SYS_SHLO('AXP76A')
		SYS_SHLO('AXP60E')
		FTP_LOG.ftp_shlo_log()
		DEL_36A_SHLO_LOG()
		COLLECT_LOG()

	except Exception as e:
		print('Err on MAIN_SYS_SHLO.')
		print(e.args)
		f = open('SYS_SHLO_LOG.TXT', 'a')
		f.write('Err on MAIN_SYS_SHLO.\n')
		f.write('time:' + str_dt + '\n')
		f.write(e.args)
		f.write('\n\n')
		f.close()
		return

	print('系統 LOCK 檢查結束...\n\n')

if __name__ == '__main__':
	MAIN_SYS_SHLO()