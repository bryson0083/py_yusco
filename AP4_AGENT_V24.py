import telnetlib
import time
import datetime
from dateutil import parser
import sqlite3

##################################################################################
# MAIN																			 #
##################################################################################
print("Executing AP4_AGENT_V24...")

USER_ID = "yucrm00"
PASSWORD = "crm120976a"
timeout = 20

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
dt2 = parser.parse(str_date).strftime("%d-%b-%Y %H").upper()
if dt2[0] == "0":
	dt2 = dt2[1:]

dt3 = parser.parse(str_date).strftime("%Y%m%d")

#紀錄執行LOG
name = "AP4_AGENT_" + dt3 + ".txt"
file = open(name, 'a', encoding = 'UTF-8')

file.write("\n\n\n*** LOG datetime  " + str(datetime.datetime.now()) + " ***\n")
file.write("執行AP4檢查...\n\n")
print("執行AP4檢查...\n")

# 建立資料庫連線
conn = sqlite3.connect('yusco.db')

# 讀取當天重啟次數
sqlstr = "select RECONNECT_CNT from AP4_AGENT "
sqlstr = sqlstr + "where "
sqlstr = sqlstr + "CHK_DATE='" + dt3 + "' "

#print(sqlstr)
cursor = conn.execute(sqlstr)
result = cursor.fetchone()

if result is not None:
	recnt = result[0]
else:
	sqlstr  = "insert into AP4_AGENT (CHK_DATE, RECONNECT_CNT) values ("
	sqlstr += "'" + dt3 + "',0)"

	try:
		conn.execute(sqlstr)
		conn.commit()
	except sqlite3.Error as er:
		print("insert AP4_AGENT RECONNECT_CNT er=" + er.args[0] + "\n")
		print(dt3 + " RECONNECT_CNT資料新增異常...Rollback!\n")
		file.write("insert AP4_AGENT RECONNECT_CNT er=" + er.args[0] + "\n")
		file.write(dt3 + " RECONNECT_CNT資料新增異常...Rollback!\n")
		conn.execute("rollback")


#delete TMP_LOG.TXT file
cmd_str = 'DEL BC5$LOG:TMP_LOG.TXT;* /NOCON\r'

tn.read_until(b"[MIS.CRM]",timeout)
tn.write(cmd_str.encode())	# string convert to bytes format

# 設定終端機型態為VT100
tn.read_until(b"[MIS.CRM]",timeout)
tn.write(b"SET TERMINAL /DEVICE=VT100\r")

# 傳輸LOG檔案名稱
log_file_name = "BC5$LOG:BC5_A4_CMU." + str(dt)

#for test
#log_file_name = "BC5$LOG:BC5_A4_CMU.0221"
#dt2 = "21-FEB-2017 21"

# 唯讀開啟傳輸LOG，大電腦中會進入VIEW檔案模式
cmd_str = "EDIT/READ " + log_file_name + " \r"

tn.read_until(b"[MIS.CRM]",timeout)
tn.write(cmd_str.encode())	# string convert to bytes format

# 把LOG寫到副本
# \x1bOS 代表按鍵PF4
tn.read_until(b"Unmodifiable | Forward",timeout)
tn.write(b"\x1bOS WRITE BC5$LOG:TMP_LOG.TXT \x1bOS\r")

# 跳出VIEW檔案模式
tn.read_until(b"written to file",timeout)
tn.write(b"\x1bOS QUIT \x1bOS\r")

#Generate searching string
sear_str = 'SEAR BC5$LOG:TMP_LOG.TXT "UT_NET_MBX_AST:  MSGTYPE =     30","' + dt2 + '" /MATCH=AND /STATISTICS\r'
disp_sear_str = 'SEAR ' + log_file_name + ' "UT_NET_MBX_AST:  MSGTYPE =     30","' + dt2 + '" /MATCH=AND /STATISTICS\r'

print(disp_sear_str)
file.write(disp_sear_str + "\n")

#waiting for prompt
tn.read_until(b"[MIS.CRM]",timeout)
tn.write(sear_str.encode())	# string convert to bytes format

cnt = 0
while True:
	line = tn.read_until(b"\r",timeout)  # Check for new line and CR
	line_str = line.decode("ASCII").replace("\n","").replace("[7m"," ").replace("[0m","")
	#print(line_str)

	if (b"Records matched:") in line:
		cnt = int(line_str[17:34].strip())
		#print("Abnormal Records matched:" + str(cnt))
		#file.write("Abnormal Records matched:" + str(cnt) + "\n\n")

	if (b"Elapsed CPU time:") in line:   # If last read line is the prompt, end loop
		break

print("V24: 目前這一小時錯誤次數=" + str(cnt))
file.write("V24: 目前這一小時錯誤次數=" + str(cnt) + "\n")

#檢視LOG同一小時內，異常次數達三次以上，進行斷線重啟一次
#若當天重啟次數已達3次，不再重啟。
if cnt > 2:
	if recnt < 3:
		print("$$$ V24: AP4出現異常，執行重啟程序. $$$\n")
		file.write("$$$ V24: AP4出現異常，執行重啟程序. $$$\n\n")
		print("執行 STOP BC5_SV\n")
		tn.read_until(b"[MIS.CRM]",timeout)
		tn.write(b"STOP BC5_SV\r")
		#tn.write(b"SHOW TIME\r")

		time.sleep(1)

		print("執行 STOP BC5_A4\n")
		tn.read_until(b"[MIS.CRM]",timeout)
		tn.write(b"STOP BC5_A4\r")
		#tn.write(b"SHOW TIME\r")

		time.sleep(5)

		print("執行 SV\n")
		tn.read_until(b"[MIS.CRM]",timeout)
		tn.write(b"SV\r")
		#tn.write(b"SHOW TIME\r")

		# 更新當天重啟次數
		recnt += 1
		sqlstr  = "update AP4_AGENT set RECONNECT_CNT = " + str(recnt) + " "
		sqlstr += "where CHK_DATE='" + dt3 + "'"

		try:
			conn.execute(sqlstr)
			conn.commit()
		except sqlite3.Error as er:
			print("update AP4_AGENT RECONNECT_CNT er=" + er.args[0] + "\n")
			print(dt3 + " RECONNECT_CNT=" + str(recnt) + "資料更新異常...Rollback!\n")
			file.write("update AP4_AGENT RECONNECT_CNT er=" + er.args[0] + "\n")
			file.write(dt3 + " RECONNECT_CNT=" + str(recnt) + "資料更新異常...Rollback!\n")
			conn.execute("rollback")
	else:
		print("當天重啟次數已達三次，不再進行重啟.\n")
		file.write("當天重啟次數已達三次，不再進行重啟.\n")
else:
	print("V24: 判斷目前傳輸無異常.\n")
	file.write("V24: 判斷目前傳輸無異常.\n")		

tn.write(b"\r")
tn.read_until(b"[MIS.CRM]",timeout)
tn.write(b"logout\r")
time.sleep(1)

file.write("*** End LOG ***\n")

# 資料庫連線關閉
conn.close()

#close connection
tn.close()

# Close File
file.close()

print("prog done..")