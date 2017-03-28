from selenium import webdriver
from datetime import date, timedelta
import time
#import cx_Oracle


chrome_path = "d:\py_yusco\chromedriver.exe" #chromedriver.exe執行檔所存在的路徑
web = webdriver.Chrome(chrome_path)

web.get('http://www.51bxg.com/web/login_register/login.aspx')
web.set_window_position(0,0) #瀏覽器位置
web.set_window_size(1024,768) #瀏覽器大小
#web.find_element_by_link_text('登录').click() 

login_name = web.find_element_by_id('login_name')
login_name.send_keys('vinceliu')
time.sleep(1)
login_password = web.find_element_by_id('login_password')
login_password.send_keys('yusco07')
#time.sleep(2)

web.find_element_by_xpath("//button[@id='login_btn']").click()
time.sleep(1)


p_date = time.strftime("%Y-%m-%d", (date.today() - timedelta(1)).timetuple())
s_date = time.strftime("%Y-%m-%d", time.localtime())

s_utilurl = "http://www.51bxg.com/web/data_center/coil_price_list.aspx?type=%E5%8D%B7&mkt=%E4%BD%9B%E5%B1%B1%E5%B8%82%E5%9C%BA&mat=304&surf=No.1&width=1500&thick=4.0&start_date=" + p_date + "&end_date=" + s_date 

def getValue():
	table = web.find_element_by_xpath("//table[@class='dc_data_list']")
	for row in table.find_elements_by_xpath(".//tr"): 
		temp_cost = [td.text for td in row.find_elements_by_xpath(".//td[@class='col6'][text()]")] 
		temp_date = [td.text for td in row.find_elements_by_xpath(".//td[@class='col7'][text()]")] 
		if (len(temp_cost)>0):
			print(temp_date[0][:10],' ',temp_cost[0][:6])

			"""
			con = cx_Oracle.connect('tqc/tqc@rp547a')
			#print(con.version)
			cursor = con.cursor()
			s_sql = "insert into market_304(market_date,lme_ni) values('20110101'," + temp_cost[0][:6] + ")"
			cursor.execute(s_sql) 
			con.commit()
			con.close()
			"""
	return

#太钢不锈 市場:佛山  材質: 304 表面:NO.1廠家:太鋼 寬度:1500 厚度:4.0
s_weburl = s_utilurl + "&fac=%E5%A4%AA%E9%92%A2%E4%B8%8D%E9%94%88"
web.get(s_weburl)
getValue()


#宝钢不锈 市場:佛山  材質: 304 表面:NO.1廠家:宔鋼 寬度:1500 厚度:4.0
#time.sleep(5)
#s_weburl = s_utilurl + "&fac=%E5%AE%9D%E9%92%A2%E4%B8%8D%E9%94%88"
#web.get(s_weburl)
#getValue()


#鞍钢联众 市場:佛山  材質: 304 表面:NO.1廠家:太鋼/宔鋼/鞍聯 寬度:1500 厚度:4.0
#time.sleep(5)
#s_weburl = s_utilurl + "&fac=%E9%9E%8D%E9%92%A2%E8%81%94%E4%BC%97"
#web.get(s_weburl)
#getValue()

#web.close()



