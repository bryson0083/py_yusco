import cx_Oracle


con = cx_Oracle.connect('tqc/tqc@rp547a')
#print(con.version)
cursor = con.cursor()
s_sql = "insert into market_304(market_date,lme_ni) values('20110102',999)"

try:
	cursor.execute(s_sql) 
	con.commit()
except cx_Oracle.DatabaseError as e:
	error, = e.args
	print("sql_code=" + str(error.code))
	print("err_msg=" + error.message)
	print("context=" + error.context)

con.close()
