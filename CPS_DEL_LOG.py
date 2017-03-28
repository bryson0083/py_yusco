import telnetlib
import time
import datetime
from dateutil.parser import parse
from dateutil import parser
from dateutil.relativedelta import relativedelta

USER_ID = "yucps00"
PASSWORD = "cps111076a"
timeout = 20

tn = telnetlib.Telnet('100.1.1.2') 

#for debug
#tn.set_debuglevel(1)

tn.read_until(b"Username: ",timeout)
tn.write(USER_ID.encode('ascii') + b"\r")

tn.read_until(b"Password: ",timeout)
tn.write(PASSWORD.encode('ascii') + b"\r")

#waiting for prompt
tn.read_until(b"[MIS.CPS]",timeout)
tn.write(b'\r')

# 由目前時間推下一個月的時間
next_dt = datetime.datetime.now() + relativedelta(months=1)
mm = parser.parse(str(next_dt)).strftime('%m')
#print(mm)

str_cmd = "DEL CPS$LOG:*_PDO_TO_COIL_AUTO." + mm + "*;* /nocon\r"
print(str_cmd)
tn.read_until(b"[MIS.CPS]",timeout)
tn.write(str_cmd.encode())	# string convert to bytes format

str_cmd = "DEL CPS$LOG:*_PDO_TO_COIL_BATCH." + mm + "*;* /nocon\r"
print(str_cmd)
tn.read_until(b"[MIS.CPS]",timeout)
tn.write(str_cmd.encode())	# string convert to bytes format

tn.read_until(b"[MIS.CPS]",timeout)
tn.write(b"logout\r")
time.sleep(1)

#close connection
tn.close()
print("prog done..")