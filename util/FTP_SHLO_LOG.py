import os
import sys
import telnetlib
import time
from ftplib import FTP
from datetime import date
from contextlib import suppress

### 以下import自行開發公用程式 ###
import util.GET_LOGIN_ID as GET_LO_ID

def writeline(data):
	global lf

	with suppress(Exception): 
		lf.write(data.encode("ISO 8859-1","replace").decode(sys.stdin.encoding))
		lf.write(os.linesep)

def ftp_shlo_log():
	global lf
	lf = None

	print("下載SHLO LOCK LOG FILE...")

	USER_ID, PASSWORD = GET_LO_ID.GET_LOGIN_ID('axp36a_dba')
	ftp = FTP("100.1.1.6", USER_ID, PASSWORD)
	org_path = "DSA1:[MIS.CPS]"
	ftp.cwd(org_path)

	ls_file = ['SHLO_60E.TXT','SHLO_76A.TXT']

	for fn in ls_file:
		filename = fn + ";1"

		try:
			lf = open(fn,"w")
			ftp.retrlines("RETR " + filename, writeline)
			lf.close()
			print("下載SHLO LOCK LOG FILE，完畢...")
		except:
			print("Err: 下載SHLO LOCK LOG FILE，失敗...")
			print(sys.exc_info())

	ftp.quit()

if __name__ == '__main__':
	ftp_shlo_log()
