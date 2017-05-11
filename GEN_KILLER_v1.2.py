import telnetlib
import time
import datetime
from dateutil import parser
import sqlite3
import json
import pandas as pd
import multiprocessing

def Chk_Gen():
	#Date format convert
	str_date = str(datetime.datetime.now())
	#str_date = "2016-12-05 02:28:12"

	dt = parser.parse(str_date).strftime("%Y%m%d")

	#紀錄執行LOG
	name = "GEN_KILLER_" + dt + ".txt"
	file = open(name, 'a', encoding = 'UTF-8')

	file.write("\n\n\n*** LOG datetime  " + str(datetime.datetime.now()) + " ***\n")

	#讀取帳密參數檔
	with open('account.json') as data_file:
		data = json.load(data_file)

	USER_ID = data['axp76a_mgr']['id']
	PASSWORD = data['axp76a_mgr']['pwd']

	#print('USER_ID=' + USER_ID)
	#print('PASSWORD=' + PASSWORD)

	timeout = 20

	###########################
	# 檢查AXP76A上GEN PROCESS #
	###########################
	file.write("執行AXP76A GEN PROCESS檢查...\n\n")
	print("執行AXP76A GEN PROCESS檢查...\n\n")
	tn = telnetlib.Telnet('100.1.1.2') 

	#for telnetlib debug
	tn.set_debuglevel(0)

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

		if state == "HIB" and (cpu_minues >= 1 or io >= 100000):
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
	file.write("執行AXP60E GEN PROCESS檢查...\n\n")
	print("執行AXP60E GEN PROCESS檢查...\n\n")
	tn = telnetlib.Telnet('100.1.1.3') 

	#for telnetlib debug
	tn.set_debuglevel(0)

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

		if state == "HIB" and (cpu_minues >= 1 or io >= 100000):
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
if __name__ == '__main__':
	#Date format convert
	str_date = str(datetime.datetime.now())

	#運行紀錄LOG
	name = "PROG_TIMEOUT.txt"
	file = open(name, 'a', encoding = 'UTF-8')

	# Start foo as a process
	p = multiprocessing.Process(target=Chk_Gen, name="Chk_Gen", args=())
	p.start()

	# Wait a maximum of 500 seconds for Chk_Gen
	# Usage: join([timeout in seconds])
	p.join(500)

	# If thread is active
	if p.is_alive():
		print(str_date + ": Timeout but Chk_Gen is running... let's kill it...")
		file.write("PROG: GEN_KILLER_v1.2 Timeout.\n")
		file.write(str_date + ": Timeout but Chk_Gen is running... let's kill it...\n\n")

		# Terminate Chk_Gen
		p.terminate()
		p.join()

	# Close File
	file.close()

	print("prog done..")