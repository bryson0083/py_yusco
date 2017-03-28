# -*- coding: utf-8 -*-
"""
Created on Tue Mar  7 10:03:29 2017

@author: bryson0083
"""

import requests
from bs4 import BeautifulSoup
import json
import re

def Login_CNCCM(s):
	#讀取帳密參數檔
	with open('account.json') as data_file:
		data = json.load(data_file)

	acc_id = data['chinaccm']['id']
	acc_pwd = data['chinaccm']['pwd']
	
	#print('acc=' + acc_id)
	#print('pwd=' + acc_pwd)

	# 登入頁面取得，__VIEWSTATE參數值
	headers = {'User-Agent':'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'}

	URL = 'http://www.chinaccm.com/'
	r = s.get(URL, headers=headers)
	r.encoding = "utf-8"
	sp = BeautifulSoup(r.text, 'html.parser')
	vws = sp.find('input', attrs={'id':'__VIEWSTATE'}).get('value')
	#print(vws)

	#網站登入
	URL  = 'http://www.chinaccm.com/MemberCenter/Login.aspx'

	payload = {
			"__VIEWSTATE": vws,
			"txtUserName": acc_id,
			"txtPassWord": acc_pwd
			}

	r = s.post(URL, data=payload, headers=headers)

	return True


def Login_51BXG(s):
	#讀取帳密參數檔
	with open('account.json') as data_file:
		data = json.load(data_file)

	acc_id = data['51bxg']['id']
	acc_pwd = data['51bxg']['pwd']
	
	#print('acc=' + acc_id)
	#print('pwd=' + acc_pwd)
	
	# 登入頁面取得，動態產生的PAGE_SESSION_ID
	headers = {'User-Agent':'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'}

	URL = 'http://www.51bxg.com/web/login_register/login.aspx'
	r = s.get(URL, headers=headers)
	r.encoding = "utf-8"
	sp = BeautifulSoup(r.text, 'lxml')
	rt_msg = str(sp.find('script', type="text/javascript"))
	#print(rt_msg)

	m = re.search('var _PAGE_SESSION_ID=[\d]+', rt_msg, flags = 0)
	pg_ssid = str(m.group()).replace("var _PAGE_SESSION_ID=","")
	#print(pg_ssid)

	#網站登入
	URL  = 'http://www.51bxg.com/api_web/WebCommon/PostUserLogin?'
	URL += 'z_access_mode=web_service&'
	URL += 'session_page_id=' + str(pg_ssid) + '&'
	URL += 'has_req_data=true&retry_num=0'

	arg_pload = '{"loginName":"' + acc_id + '","loginPwd":"' + acc_pwd + '","autoLogin":false}'

	payload = {
			"z_data": arg_pload
			}
	
	r = s.post(URL, data=payload, headers=headers)
	r.encoding = "utf-8"
	sp = BeautifulSoup(r.text, 'html.parser')
	#print(sp)

	flag = r.text.find('登录成功')
	#print(flag)

	if flag > 0:
		return True
	else:
		return False

def Logout_MTP(s):
	print("Logout LME")
	headers = {'User-Agent':'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'}
	#session = requests.session()
	
	s.get("https://www.metalprices.com/a/Logout", headers=headers)
	s.keep_alive = False
	#print(r.text)

def Login_MTP(s):
	#讀取帳密參數檔
	with open('account.json') as data_file:
		data = json.load(data_file)

	acc_id = data['lme']['id']
	acc_pwd = data['lme']['pwd']
	
	#print('acc=' + acc_id)
	#print('pwd=' + acc_pwd)
	
	# 登入網站
	headers = {'User-Agent':'User-Agent:Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'}

	# s 為傳入的requests物件
	#s.headers.update(headers)

	URL = 'https://www.metalprices.com/a/Login'
	
	payload = {
			"IsMobile": "False",
			"Username": acc_id,
			"Password": acc_pwd,
			"remember": "false"
			}
	
	r = s.post(URL, data=payload, headers=headers)
	r.encoding = "utf-8"
	sp = BeautifulSoup(r.text, 'html.parser')
	#print(sp)

	rt_msg = str(sp.find('p'))
	flag = rt_msg.find('Your account is currently logged into the website')
	#print('\n\nflag=' + str(flag))
	
	if flag > 0:
		#目前已有登入網站的連線，要先排除其他已連線的設備
		#原網站這時會有一個switch device的按鈕
		#print("已有登入連線")

		URL2 = 'https://www.metalprices.com/a/switchdevice?returnUrl=%2F'
		payload = {
			"mobile": "no"
		}
		r = s.post(URL2, data=payload, headers=headers)
		r.encoding = "utf-8"
		
		sp = BeautifulSoup(r.text, 'html.parser')

	#分析目前回傳的網頁文件，是否<title>標籤內含"Custom Dashboard"
	#用以識別是否有正確登入網站
	rt_msg = str(sp.find('title'))
	flag = rt_msg.find('Custom Dashboard')

	if flag > 0:
		#print('登入成功.')
		return True

	else:
		#print('登入失敗.')
		return False