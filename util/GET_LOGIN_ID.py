# -*- coding: utf-8 -*-
"""
讀取帳號密碼公用程式

@author: Bryson Xue

@Note: 
	根據傳入參數，回傳帳號、密碼  

"""
import json

def GET_LOGIN_ID(arg_acc=""):
	#讀取帳密參數檔
	with open('account.json') as data_file:
		data = json.load(data_file)

	USER_ID = ""
	PASSWORD = ""
	if arg_acc == "":
		print("Err: GET_LOGIN_ID無輸入參數.")
	else:
		try:
			USER_ID = data[arg_acc]['id']
			PASSWORD = data[arg_acc]['pwd']
		except Exception as e:
			print("Err: Call GET_LOGIN_ID('" + arg_acc + "')讀取參數錯誤.")
			print(e.args)

	return USER_ID, PASSWORD

if __name__ == '__main__':
	GET_LOGIN_ID()