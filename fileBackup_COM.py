# _*_ coding: utf-8 _*_

from ftplib import FTP
from contextlib import suppress
from datetime import date
import sys
import os

lf = None

def writeline(data):
	with suppress(Exception): 
		lf.write(data.encode("ISO 8859-1","replace").decode(sys.stdin.encoding))
		lf.write(os.linesep)

def getFile(ftp, org_path, arg_path, filename):
	win_path = "d:\py_yusco\yusco"
	try:
		s_today = str(date.today()).replace("-","")
		root_paths = os.path.join(win_path,s_today) 
		file_path = os.path.join(root_paths,arg_path)
		if not os.path.exists(file_path):
			os.makedirs(file_path)
		local_filename = os.path.join(file_path, filename)
		ftp.cwd(org_path)

		global lf
		lf = open(local_filename,"w")
		ftp.retrlines("RETR " + filename, writeline)
		lf.close()

	except:
		print(sys.exc_info())

def find_str(s,char):
	index = 0
	if char in s:
		c = char[0]
		for ch in s:
			if ch == c:
				if s[index:index+len(char)] == char:
					return index
			index += 1
	return -1

def search_file(arg_type):
	global org_path
	org_path = "DSA1:[MIS]"
	root_path = "DSA1:[MIS."

	ftp.cwd(org_path)
	data = []
	cmd_text = 'LIST [...]*' + arg_type 
	ftp.retrlines(cmd_text,data.append)
#	ftp.dir('[...]*.QTS',data.append)

	filename = ""
	lineData = []
	for line in data:
		lineData = line.split()
		if len(lineData) > 0:
			pos_index = find_str(lineData[0],arg_type)
			if lineData[0]=="Directory":
				file_path = ""
	#			print(lines[dir_begin:])
				org_path = lineData[1]
				now_path = lineData[1][len(root_path):len(lineData[1])-1].split('.')
				print(org_path, "-", now_path, "-")
				i=1
				for aa in now_path:
					file_path = os.path.join(file_path,aa)
#				print(file_path)
			if pos_index >= 0  and now_path[0] != 'USER' and filename != lineData[0][:pos_index+len(arg_type)]:
				getFile(ftp,org_path,file_path,lineData[0][:pos_index+len(arg_type)])
				filename = lineData[0][:pos_index+len(arg_type)] 
				print(filename)

ftp = FTP("100.1.1.6","yudba00","dba0802")
file_type = "." + sys.argv[1]
print(file_type)
search_file(file_type)
ftp.quit()