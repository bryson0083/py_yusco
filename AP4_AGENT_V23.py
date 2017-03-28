import telnetlib
import time
import datetime
from dateutil import parser
import sqlite3

##################################################################################
# MAIN																			 #
##################################################################################
USER_ID = "yucrm00"
PASSWORD = "crm120976a"
timeout = 20

tn = telnetlib.Telnet('100.1.1.2') 

#for telnetlib debug
tn.set_debuglevel(1)

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

tn.read_until(b"[MIS.CRM]",timeout)
tn.write(b"SET TERMINAL /DEVICE=VT100\r")

tn.read_until(b"[MIS.CRM]",timeout)
tn.write(b"EDIT/READ BC5$LOG:BC5_A4_CMU.0223 \r")

tn.read_until(b"Unmodifiable | Forward",timeout)
tn.write(b"\x1bOS WRITE BC5$LOG:TMP_LOG.TXT \x1bOS\r")

tn.read_until(b"written to file",timeout)
tn.write(b"\x1bOS QUIT \x1bOS\r")

tn.write(b"\r")
tn.read_until(b"[MIS.CRM]",timeout)
tn.write(b"logout\r")
time.sleep(1)

file.write("*** End LOG ***\n")

#close connection
tn.close()

# Close File
file.close()

print("prog done..")