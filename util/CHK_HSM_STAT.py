# -*- coding: utf-8 -*-
"""
熱軋HSM產線運作狀況

@author: Bryson Xue

@Note: 
	確認產線HSM是否運行中，並回傳代碼(1運轉, 0停機, 99:不明錯誤)

"""
import pyodbc 
import os

### 以下import自行開發公用程式 ###
import util.GET_LOGIN_ID as GET_LO_ID

def CHK_HSM_STAT():
	print("Executing " + os.path.basename(__file__) + "...")

	USER_ID, PASSWORD = GET_LO_ID.GET_LOGIN_ID('axp76a_crm')

	#連RDB
	conn = pyodbc.connect(r'DSN=RDBPCM60;UID=' + USER_ID +';PWD=' + PASSWORD)

	sql_str = "select STATUS_CODE, STATUS_EXPLAIN from pcmb204m where ename = 'HSM'"

	try:
		cursor = conn.cursor()
		cursor.execute(sql_str)

		for row in cursor:
			#print(row)
			stat_code = row[0]			#狀態(1運轉0停機)
			stat_desc = row[1].strip()	#狀態描述

		print("CHK_HSM_STAT: 檢查目前HSM產線狀態為:" + stat_desc)
		#print(stat_code)

	except Exception as e:
		stat_code = 99	#出現任何錯誤，狀態碼設定為99
		print("Err: HSM產線運作狀況讀取失敗.")
		print(e.args)

	#關閉資料庫連線
	conn.close()

	return stat_code

if __name__ == '__main__':
	CHK_HSM_STAT()