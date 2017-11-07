import telnetlib
import time
import datetime
from dateutil.parser import parse
from dateutil import parser
from dateutil.relativedelta import relativedelta
import json

def DEL_CRM_LOG():
	print("執行CRM LOG舊檔案刪除作業...\n")

	#讀取帳密參數檔
	with open('account.json') as data_file:
		data = json.load(data_file)

	USER_ID = data['axp76a_crm']['id']
	PASSWORD = data['axp76a_crm']['pwd']
	timeout = 20

	tn = telnetlib.Telnet('100.1.1.2') 

	#for debug
	#tn.set_debuglevel(1)

	tn.read_until(b"Username: ",timeout)
	tn.write(USER_ID.encode('ascii') + b"\r")

	tn.read_until(b"Password: ",timeout)
	tn.write(PASSWORD.encode('ascii') + b"\r")

	#waiting for prompt
	tn.read_until(b"[MIS.CRM]",timeout)
	tn.write(b'\r')

	# 由目前時間推下一個月的時間
	next_dt = datetime.datetime.now() + relativedelta(months=1)
	mm = parser.parse(str(next_dt)).strftime('%m')
	#print(mm)

	str_cmd = "DEL BC5$LOG:*." + mm + "*;* /nocon\r"
	print(str_cmd)
	tn.read_until(b"[MIS.CRM]",timeout)
	tn.write(str_cmd.encode())	# string convert to bytes format

	tn.read_until(b"[MIS.CRM]",timeout)
	tn.write(b"logout\r")
	time.sleep(1)

	#close connection
	tn.close()
	print("本次CRM LOG舊檔案刪除作業結束，等待下次執行...\n\n\n")


##################################################################################
# MAIN																			 #
##################################################################################
if __name__ == '__main__':
	DEL_CRM_LOG()