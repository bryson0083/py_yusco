import telnetlib
import time
import datetime
from dateutil import parser
import json
import pandas as pd
import multiprocessing

def Chk_Err1003():
	#讀取帳密參數檔
	with open('account.json') as data_file:
		data = json.load(data_file)

	USER_ID = data['axp76a_crm']['id']
	PASSWORD = data['axp76a_crm']['pwd']
	timeout = 20

	#連線大電腦AXP76A
	tn = telnetlib.Telnet('100.1.1.2') 

	#for telnetlib debug
	#tn.set_debuglevel(1)

	tn.read_until(b"Username: ",timeout)
	tn.write(USER_ID.encode('ascii') + b"\r")

	tn.read_until(b"Password: ",timeout)
	tn.write(PASSWORD.encode('ascii') + b"\r")

	#Date format convert
	str_date = str(datetime.datetime.now())
	#str_date = "2016-12-05 02:28:12"

	dt  = parser.parse(str_date).strftime('%m%d')
	dt2 = parser.parse(str_date).strftime("%Y%m%d")
	dt3 = parser.parse(str_date).strftime("%d-%b-%Y %H:%M").upper()
	if dt3[0] == "0":
		dt3 = dt3[1:]

	#以當下的時間，往前推10分鐘的日期時間，搜尋SQL CODE=-1003錯誤。
	chk_dt_ls = []
	for i in range(0,10,1):
		tmp_date = parser.parse(str_date).strftime("%Y/%m/%d %H:%M")
		date_1 = datetime.datetime.strptime(tmp_date, "%Y/%m/%d %H:%M")
		tmp_date = date_1 + datetime.timedelta(minutes=-i)
		tmp_date = str(tmp_date)[0:16]
		tmp_date = parser.parse(tmp_date).strftime("%d-%b-%Y %H:%M")
		if tmp_date[0] == "0":
			tmp_date = tmp_date[1:]

		chk_dt_ls.append(tmp_date)

	#運行紀錄LOG
	name = "AP4_SEAR_1003_" + dt2 + ".txt"
	file = open(name, 'a', encoding = 'UTF-8')

	file.write("\n\n\n*** LOG datetime  " + str(datetime.datetime.now()) + " ***\n")
	file.write("V1.1: 執行AP4 SQL CODE -1003檢查...\n\n")

	cnt = 0
	for chk_dt in chk_dt_ls:
		#Generate searching string
		sear_str = 'SEAR BC5$LOG:BC5_A4_CMU.' + dt + ' "Store A4_PDO in RDB failed","-1003","' + chk_dt + '" /MATCH=AND /STATISTICS\r'
		file.write(sear_str + "\n")
		print(sear_str)

		#waiting for prompt
		tn.read_until(b"[MIS.CRM]",timeout)
		tn.write(sear_str.encode())	# string convert to bytes format

		while True:
			line = tn.read_until(b"\r",timeout)  # Check for new line and CR
			line_str = line.decode("ASCII").replace("\n","").replace("[7m"," ").replace("[0m","")
			#print(line_str)

			if (b"Records matched:") in line:
				cnt = int(line_str[17:34].strip())
				print("Searching Result Records matched:" + str(cnt))
				file.write("Searching Result Records matched:" + str(cnt) + "\n\n")

			if (b"Elapsed CPU time:") in line:   # If last read line is the prompt, end loop
				break

		#如果有找到，就不繼續找下去
		#print("檢查結果 cnt=" + str(cnt) + "\n")
		if cnt > 0:
			break

	#搜尋時間區間若有出現SQLCODE=-1003錯誤
	if cnt > 0:
		print("$$$ APL4出現PDO寫入RDB -1003錯誤. $$$\n\n")
		file.write("$$$ APL4出現PDO寫入RDB -1003錯誤. $$$\n\n")
	else:
		print("目前AP4正常.\n\n")
		file.write("目前AP4正常.\n\n")

	tn.read_until(b"[MIS.CRM]",timeout)
	tn.write(b"logout\r")

	#close connection
	tn.close()


	#若出現-1003錯誤，開始進行76A、60E上，狀態HIB PROCESS排除
	#以MGR身分登入系統進行處理
	USER_ID = data['axp76a_mgr']['id']
	PASSWORD = data['axp76a_mgr']['pwd']
	if cnt > 0:
	#if cnt == 0:
		###########################
		# 檢查AXP76A上GEN PROCESS #
		###########################
		file.write("執行AXP76A GEN狀態HIB PROCESS排除...\n\n")
		print("執行AXP76A GEN狀態HIB PROCESS排除...\n\n")
		tn = telnetlib.Telnet('100.1.1.2') 

		#for telnetlib debug
		#tn.set_debuglevel(0)

		tn.read_until(b"Username: ",timeout)
		tn.write(USER_ID.encode('ascii') + b"\r")

		tn.read_until(b"Password: ",timeout)
		tn.write(PASSWORD.encode('ascii') + b"\r")

		tn.read_until(b"[MIS.MGR]",timeout)
		tn.write(b"SH SYSTEM /PROC=GENERI*\r")

		i=0
		data = []
		while True:
			line = tn.read_until(b"\r",timeout)  # Check for new line and CR
			line_str = line.decode("ASCII").replace("\n","")
			#print(line_str)

			if i > 2:
				rdata = line_str.split(" ")
				rdata = [elem for elem in rdata if len(elem) > 0]
				rdata = [elem for elem in rdata if elem != "\r"]
				#print(rdata)

				if len(rdata) > 3:
					data.append(rdata)

			if (b"[MIS.MGR]") in line:   # If last read line is the prompt, end loop
				break

			i += 1

		df = pd.DataFrame(data, columns=["Pid","Process Name","State","Pri","I/O","A","CPU","Page flts","Pages"])
		#print(df)

		for i in range(0,len(df)):
			pid = df['Pid'][i]
			state = df['State'][i]
			io = int(df['I/O'][i])
			cpu = df['CPU'][i]
			cpu_tmp = cpu.split(".")[0].split(":")
			cpu_minues = int(cpu_tmp[0]) * 60 + int(cpu_tmp[1])
			#print(str(pid) + " " + state + " " + cpu + " " + str(cpu_minues))

			if state == "HIB":
				print(str(pid) + " " + state + " " + str(io) + " " + cpu + " " + str(cpu_minues))
				file.write(str(pid) + " " + state + " " + str(io) + " " + cpu + " " + str(cpu_minues) + "\n")
				print("STOP /ID=" + str(pid) + "\n")
				file.write("STOP /ID=" + str(pid) + "\n")

				cmd = "STOP /ID=" + str(pid) + "\r"
				tn.read_until(b"[MIS.MGR]",timeout)
				tn.write(cmd.encode())
				time.sleep(2)

		tn.write(b"\r")
		tn.read_until(b"[MIS.MGR]",timeout)
		tn.write(b"logout\r")
		time.sleep(1)

		#close connection
		tn.close()

		###########################
		# 檢查AXP60E上GEN PROCESS #
		###########################
		file.write("執行AXP60E GEN狀態HIB PROCESS排除...\n\n")
		print("執行AXP60E GEN狀態HIB PROCESS排除...\n\n")
		tn = telnetlib.Telnet('100.1.1.3') 

		#for telnetlib debug
		#tn.set_debuglevel(0)

		tn.read_until(b"Username: ",timeout)
		tn.write(USER_ID.encode('ascii') + b"\r")

		tn.read_until(b"Password: ",timeout)
		tn.write(PASSWORD.encode('ascii') + b"\r")

		tn.read_until(b"[MIS.MGR]",timeout)
		tn.write(b"SH SYSTEM /PROC=GENERI*\r")

		i=0
		data = []
		while True:
			line = tn.read_until(b"\r",timeout)  # Check for new line and CR
			line_str = line.decode("ASCII").replace("\n","")
			#print(line_str)

			if i > 2:
				rdata = line_str.split(" ")
				rdata = [elem for elem in rdata if len(elem) > 0]
				rdata = [elem for elem in rdata if elem != "\r"]
				#print(rdata)

				if len(rdata) > 3:
					data.append(rdata)

			if (b"[MIS.MGR]") in line:   # If last read line is the prompt, end loop
				break

			i += 1

		df = pd.DataFrame(data, columns=["Pid","Process Name","State","Pri","I/O","A","CPU","Page flts","Pages"])
		#print(df)

		for i in range(0,len(df)):
			pid = df['Pid'][i]
			state = df['State'][i]
			io = int(df['I/O'][i])
			cpu = df['CPU'][i]
			cpu_tmp = cpu.split(".")[0].split(":")
			cpu_minues = int(cpu_tmp[0]) * 60 + int(cpu_tmp[1])
			#print(str(pid) + " " + state + " " + cpu + " " + str(cpu_minues))

			if state == "HIB":
				print(str(pid) + " " + state + " " + str(io) + " " + cpu + " " + str(cpu_minues))
				file.write(str(pid) + " " + state + " " + str(io) + " " + cpu + " " + str(cpu_minues) + "\n")
				print("STOP /ID=" + str(pid) + "\n")
				file.write("STOP /ID=" + str(pid) + "\n")

				cmd = "STOP /ID=" + str(pid) + "\r"
				tn.read_until(b"[MIS.MGR]",timeout)
				tn.write(cmd.encode())
				time.sleep(2)

		tn.write(b"\r")
		tn.read_until(b"[MIS.MGR]",timeout)
		tn.write(b"logout\r")
		time.sleep(1)

		#close connection
		tn.close()


	file.write("*** End LOG ***\n")

	# Close File
	file.close()

##################################################################################
# MAIN																			 #
##################################################################################
def MAIN_CHK_Err1003():
#if __name__ == '__main__':
	print("執行MAIN_CHK_Err1003進行AP4 RDB -1003錯誤偵測...\n")

	#Date format convert
	str_date = str(datetime.datetime.now())

	#運行紀錄LOG
	name = "PROG_TIMEOUT.txt"
	file = open(name, 'a', encoding = 'UTF-8')

	# Start foo as a process
	p = multiprocessing.Process(target=Chk_Err1003, name="Chk_Err1003", args=())
	p.start()

	# Wait a maximum of 500 seconds for Chk_Err1003
	# Usage: join([timeout in seconds])
	p.join(500)

	# If thread is active
	if p.is_alive():
		print(str_date + ": Timeout but Chk_Err1003 is running... let's kill it...")
		file.write("PROG: AP4_SEAR_1003_V1.3 Timeout.\n")
		file.write(str_date + ": Timeout but Chk_Err1003 is running... let's kill it...\n\n")

		# Terminate Chk_Err1003
		p.terminate()
		p.join()

	# Close File
	file.close()

	print("本次AP4 RDB -1003錯誤檢查結束，等待下次執行...\n\n\n")