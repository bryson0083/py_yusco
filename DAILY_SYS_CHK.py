import telnetlib
import time
import json

def DAILY_SYS_CHK():
	print("執行STA每日系統檢查作業...\n")

	#讀取帳密參數檔
	with open('account.json') as data_file:
		data = json.load(data_file)

	USER_ID = data['axp76a_sta']['id']
	PASSWORD = data['axp76a_sta']['pwd']
	timeout = 20

	tn = telnetlib.Telnet('100.1.1.2') 

	#for debug
	#tn.set_debuglevel(1)

	tn.read_until(b"Username: ",timeout)
	tn.write(USER_ID.encode('ascii') + b"\r")

	tn.read_until(b"Password: ",timeout)
	tn.write(PASSWORD.encode('ascii') + b"\r")

	#waiting for prompt
	tn.read_until(b"[MIS.STA]",timeout)
	tn.write(b'\r')

	str_cmd = "ck\r"
	print(str_cmd)
	tn.read_until(b"[MIS.STA]",timeout)
	tn.write(str_cmd.encode())	# string convert to bytes format

	tn.read_until(b"[MIS.STA]",timeout)
	tn.write(b"logout\r")
	time.sleep(1)

	#close connection
	tn.close()
	print("STA每日系統檢查作業結束，等待下次執行...\n\n\n")

##################################################################################
# MAIN																			 #
##################################################################################
if __name__ == '__main__':
	DAILY_SYS_CHK()