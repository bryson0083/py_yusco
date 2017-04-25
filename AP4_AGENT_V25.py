import telnetlib
import time
import datetime
from dateutil import parser
import sqlite3
import json

##################################################################################
# MAIN																			 #
##################################################################################
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

#因大電腦系統與電腦的系統時間存在時差，大約比電腦時間慢2分鐘，
#因此產生search string時，需要往前後推個幾分鐘作為搜尋範圍。
#以當下的時間，往前推3分鐘與往後推2分鐘的日期時間
chk_dt_ls = []
i=-3
for i in range(-3,3,1):
	tmp_date = parser.parse(str_date).strftime("%Y/%m/%d %H:%M")
	date_1 = datetime.datetime.strptime(tmp_date, "%Y/%m/%d %H:%M")
	tmp_date = date_1 + datetime.timedelta(minutes=i)
	tmp_date = str(tmp_date)[0:16]
	tmp_date = parser.parse(tmp_date).strftime("%d-%b-%Y %H:%M")
	if tmp_date[0] == "0":
		tmp_date = tmp_date[1:]

	chk_dt_ls.append(tmp_date)

#運行紀錄LOG
name = "AP4_AGENT_" + dt2 + ".txt"
file = open(name, 'a', encoding = 'UTF-8')

file.write("\n\n\n*** LOG datetime  " + str(datetime.datetime.now()) + " ***\n")
file.write("執行AP4檢查...\n\n")

# 建立資料庫連線
conn = sqlite3.connect('yusco.db')

# 讀取當天重啟次數
sqlstr = "select RECONNECT_CNT from AP4_AGENT "
sqlstr = sqlstr + "where "
sqlstr = sqlstr + "CHK_DATE='" + dt2 + "' "

#print(sqlstr)
cursor = conn.execute(sqlstr)
result = cursor.fetchone()

if result is not None:
	recnt = result[0]
else:
	sqlstr  = "insert into AP4_AGENT (CHK_DATE, RECONNECT_CNT) values ("
	sqlstr += "'" + dt2 + "',0)"

	try:
		conn.execute(sqlstr)
		conn.commit()
	except sqlite3.Error as er:
		print("insert AP4_AGENT RECONNECT_CNT er=" + er.args[0] + "\n")
		print(dt2 + " RECONNECT_CNT資料新增異常...Rollback!\n")
		file.write("insert AP4_AGENT RECONNECT_CNT er=" + er.args[0] + "\n")
		file.write(dt2 + " RECONNECT_CNT資料新增異常...Rollback!\n")
		conn.execute("rollback")


#進入CRM下AP4傳輸console，發送測試訊息
print("進入CRM下AP4傳輸console，發送測試訊息.")
sear_str = 'sv_a4\r'
#file.write(sear_str + "\n")

#waiting for prompt
tn.read_until(b"[MIS.CRM]",timeout)
tn.write(sear_str.encode())	# string convert to bytes format

send_yn = "N"
while True:
	line = tn.read_until(b"\r",timeout)  # Check for new line and CR
	line_str = line.decode("ASCII")
	#print(line_str)

	if (b"Your choice is :") in line:
		if send_yn == "Y": 
			tn.write(b"Q\r")
			print("**Quit AP4 console.\n")
			break	
		else:
			tn.write(b"1 \r")
			print("**Send AP4 net test msg.\n")
			send_yn = "Y"

#發送測試訊息後，休眠20秒，等待回傳測試結果
print("已發送test msg，休眠20秒，等待回傳結果.")
time.sleep(20)
print("休眠結束，進行傳輸net test回傳訊息檢查.")

cnt = 0
for chk_dt in chk_dt_ls:
	#Generate searching string
	sear_str = 'SEAR BC5$LOG:BC5_A4_CMU.' + dt + ' "net test positive acknowledge (A)","' + chk_dt + '" /MATCH=AND /STATISTICS\r'
	file.write(sear_str + "\n")
	#print(sear_str)

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

#檢視LOG若發送出的測試訊息，有收到回傳回來的Ack A訊息，表示傳輸正常
#若完全都沒有收到回傳的訊息，則cnt=0，視為傳輸以掛掉，進行重啟動作。
#若當天重啟次數已達3次，不再重啟。
if cnt == 0:
	if recnt < 3:
		print("$$$ V25: AP4出現異常，執行重啟程序. $$$\n")
		file.write("$$$ V25: AP4出現異常，執行重啟程序. $$$\n\n")
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
		sqlstr += "where CHK_DATE='" + dt2 + "'"

		try:
			conn.execute(sqlstr)
			conn.commit()
		except sqlite3.Error as er:
			print("update AP4_AGENT RECONNECT_CNT er=" + er.args[0] + "\n")
			print(dt2 + " RECONNECT_CNT=" + str(recnt) + "資料更新異常...Rollback!\n")
			file.write("update AP4_AGENT RECONNECT_CNT er=" + er.args[0] + "\n")
			file.write(dt2 + " RECONNECT_CNT=" + str(recnt) + "資料更新異常...Rollback!\n")
			conn.execute("rollback")
	else:
		print("當天重啟次數已達三次，不再進行重啟.\n")
		file.write("當天重啟次數已達三次，不再進行重啟.\n")
else:
	print("V25: 判斷目前傳輸無異常.\n")
	file.write("V25: 判斷目前傳輸無異常.\n")	

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