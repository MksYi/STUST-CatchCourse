# -*- coding: utf-8 -*-
import os, requests, bs4, urllib, MySQLdb, datetime, time, threading

class catch_all_class_status(threading.Thread):
	def __init__(self, className):
		self._className = className;

		self.headers = {
			'Host':'course.stust.edu.tw',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:56.0) Gecko/20100101 Firefox/56.0',
			'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
			'Accept-Language':'en-GB,en;q=0.5',
			'Accept-Encoding':'gzip, deflate',
			'Content-Type':'application/x-www-form-urlencoded',
			'Content-Length':'24805',
		}
		self.url = "http://course.stust.edu.tw/CourSel/Pages/QueryAndSelect.aspx"
		self.session = requests.session()
		self.__VIEWSTATE = ''
		self.__EVENTVALIDATION = ''
		self.page = 1;
		self.selectList = ["02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12", "13", "14" ,"15", "16", "17", "18", "19", "20", "21"];
		self.classification = 	{	
									"人文藝術領域":"01L00",
									"人文經典類":"01L01",
									"藝術美學類":"01L02",
									"哲學思維類":"01L03",
									"歷史文明類":"01L04",
									"社會科學領域":"01M00",
									"歷史文化類":"01M01",
									"法政與社會類":"01M02",
									"商管經濟類":"01M03",
									"自然科學領域":"01N00",
									"科技與社會類":"01N01",
									"生命科學類":"01N02",
									"實證與推理類":"01N03",
									"綜合實踐領域":"01P01"
								}
		super().__init__()
		pass

	def run(self):
		# >> initialize Start <<
		self.__getSelectClassPageData();
		# >> initialize End <<

		courseCount, courseData = self.__getImportPostData(self._className);
		self.__getCourseDataNumber(courseCount, courseData);

		if self.page == 2:
			courseCount, courseData = self.__getImportPostData(self._className);
			self.__getCourseDataNumber(courseCount, courseData);
			self.__getPageInitialize(self._className);
			self.page = 1;

	def __getCourseDataNumber(self, courseCount, courseData):
		for count in range(courseCount):
			PostData = {
				'__EVENTTARGET':'ctl00$ContentPlaceHolder1$GridView1$ctl' + self.selectList[count] + '$LinkButton1',
				'__EVENTARGUMENT':'',
				'__LASTFOCUS':'',
				'__VIEWSTATE': self.__VIEWSTATE,
				'__VIEWSTATEENCRYPTED':'',
				'__EVENTVALIDATION': self.__EVENTVALIDATION,
			}
			response = self.session.post(self.url, data=PostData, headers=self.headers)
			data = bs4.BeautifulSoup(response.text, "html.parser")

			# 課程代碼
			courseData[count]['課程代碼'] = data.find(id="ctl00_ContentPlaceHolder1_CourseDetail_onepage1_lab_subcode").text
			# 課程名稱
			courseData[count]['課程名稱'] = data.find(id="ctl00_ContentPlaceHolder1_CourseDetail_onepage1_lab_subname_ch").text
			# 任課教師
			courseData[count]['任課教師']
			# 課程學分
			courseData[count]['學分']
			# 課程領域
			courseData[count]['課程領域']
			# 上課時間
			courseData[count]['上課時間']
			# 總人數上限
			courseData[count]['總人數上限'] = data.find(id="ctl00_ContentPlaceHolder1_CourseDetail_onepage1_lab_count11").text
			# 目前選課人數
			courseData[count]['目前選課人數'] = data.find(id="ctl00_ContentPlaceHolder1_CourseDetail_onepage1_lab_count12").text
			# 抓取資料時間 '2018-02-25 16:33:50'
			courseData[count]['抓取時間'] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

			print("=" * 80)
			print(courseData[count])
			# self.__saveToMySQL(courseData[count])
		pass


	def __saveToMySQL(self, courseData):
		db_host = ''
		db_account = '';
		db_password = '';
		db_name = ''

		# 連接到 MySQL
		db = MySQLdb.connect(host=db_host, user=db_account, passwd=db_password, db=db_name ,charset='utf8')
		cursor = db.cursor()

		# 判斷是否存在
		if cursor.execute("SELECT course_total_people, course_current_people FROM course_data WHERE course_name = '{0}'".format(courseData['課程名稱'])):

			# 判斷是否需要更新
			data = cursor.fetchone()
			if courseData['總人數上限'] != data[0] or courseData['目前選課人數'] != data[1]:
				sql = "UPDATE course_data SET course_total_people = '{0}', course_current_people = '{1}', catch_time = '{2}' WHERE course_name = '{3}'".format(courseData['總人數上限'], courseData['目前選課人數'], courseData['抓取時間'], courseData['課程名稱'])
			else:
			# 資料存在且沒異動
				print("Nothing to do");
				return 0;

		else:
		# 沒有資料則新增
			sql = "INSERT INTO course_data(course_code, course_name, course_tearcher, course_credit, classification, course_lesson, course_total_people, course_current_people, catch_time) VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}')".format(courseData['課程代碼'], courseData['課程名稱'], courseData['任課教師'], courseData['學分'][0:1], courseData['課程領域'], courseData['上課時間'], courseData['總人數上限'], courseData['目前選課人數'], courseData['抓取時間'])

		try:
			print("-" * 80)
			print(sql)
			# 執行 SQL 語句
			cursor.execute(sql)
			# 提交
			db.commit()
		except Exception as e:
			print(e)

		pass

	def __getPageInitialize(self, courseName):
		print("=" * 40);
		print("Post DATA Page Initialize" + courseName)
		print("=" * 40);

		DATA = {
			'__EVENTARGUMENT':'Page$1',
			'__EVENTTARGET':'ctl00$ContentPlaceHolder1$GridView1',
			'__LASTFOCUS':'',
			'__VIEWSTATE': self.__VIEWSTATE,
			'__VIEWSTATEENCRYPTED':'',
			'__EVENTVALIDATION': self.__EVENTVALIDATION,
			'ctl00$ContentPlaceHolder1$TabContainer1$TabPanel1$lbox_general':self.classification[courseName]
		}
		response = self.session.post(self.url, data= DATA, headers=self.headers)
		data = bs4.BeautifulSoup(response.text, "html.parser")

		data_out = data.find_all(type='hidden')
		try:
			if data_out[5]['value'] != '' and data_out[8]['value'] != '':
				self.__VIEWSTATE = data_out[5]['value']
				self.__EVENTVALIDATION = data_out[8]['value']
			else:
				quit()
		except:
			quit()
		pass



	def __isTwoPage(self, trCount):
		#資料比數 Max = 20; 標題有一個 tr; page 有兩個 tr
		if(trCount>=23):
			return True;
		else:
			return False;
		pass


	def __getImportPostData(self, courseName):
		print("=" * 40)
		print("Post DATA Page:" + str(self.page) + "  " + courseName)
		print("=" * 40)

		if self.page == 1:
			DATA = {
				'__EVENTARGUMENT':'Page$1',
				'__EVENTTARGET':'ctl00$ContentPlaceHolder1$TabContainer1$TabPanel1$lbox_general',
				'__LASTFOCUS':'',
				'__VIEWSTATE': self.__VIEWSTATE,
				'__VIEWSTATEENCRYPTED':'',
				'__EVENTVALIDATION': self.__EVENTVALIDATION,
				'ctl00$ContentPlaceHolder1$TabContainer1$TabPanel1$lbox_general':self.classification[courseName]
			}
		elif self.page == 2:
			DATA = {
				'__EVENTARGUMENT':'Page$2',
				'__EVENTTARGET':'ctl00$ContentPlaceHolder1$GridView1',
				'__LASTFOCUS':'',
				'__VIEWSTATE': self.__VIEWSTATE,
				'__VIEWSTATEENCRYPTED':'',
				'__EVENTVALIDATION': self.__EVENTVALIDATION,
				'ctl00$ContentPlaceHolder1$TabContainer1$TabPanel1$lbox_general':self.classification[courseName]
			}
		else:
			quit()

		response = self.session.post(self.url, data= DATA, headers=self.headers)
		data = bs4.BeautifulSoup(response.text, "html.parser")

		table = data.find(id="ctl00_ContentPlaceHolder1_GridView1")
		courseCount = len(table.find_all("tr"))
		if self.page == 1:
			if(self.__isTwoPage(courseCount)):
				# A Page Data MAX = 20
				courseCount = 20;
				self.page = 2;
			else:
				# 扣除 title 的 tr
				courseCount = courseCount - 1;
				self.page = 1;
		elif self.page == 2:
			# title 1 tr || page 2 tr 所以減 3
			courseCount = courseCount - 3;

		table = table.find_all("tr");
		courseData = [{"課程代碼":"", "課程名稱":"", "任課教師":"", "學分":"", "課程領域":"", "上課時間":"", "總人數上限":"", "目前選課人數":"", "抓取時間":""} for i in range(courseCount)]
		i = 0
		for courseDataTmp in table:
			courseDataTmp = courseDataTmp.find_all("td")
			try:
				#0是否選課	1重補修代碼	2課程名稱	[3學分]	[4任課教師]	5必選修	[6課程領域]	[7時間]
				courseData[i]['學分'] = courseDataTmp[3].text.replace("\r\n","").strip()
				courseData[i]['任課教師'] = courseDataTmp[4].text.replace("\r\n","").strip()
				courseData[i]['課程領域'] = courseDataTmp[6].text.replace("\r\n","").strip()
				courseData[i]['上課時間'] = courseDataTmp[7].text.replace("\r\n","").strip()
				i = i + 1;
			except:
				pass

		data_out = data.find_all(type='hidden')
		try:
			if data_out[5]['value'] != '' and data_out[8]['value'] != '':
				self.__VIEWSTATE = data_out[5]['value']
				self.__EVENTVALIDATION = data_out[8]['value']
			else:
				quit()
		except:
			quit()

		return (courseCount, courseData);

	def __getSelectClassPageData(self):
		response = self.session.get(self.url)
		data = bs4.BeautifulSoup(response.text, "html.parser")
		data_out = data.find_all(type='hidden')
		
		__VIEWSTATE = ''
		__EVENTVALIDATION = ''
		try:
			__VIEWSTATE = data_out[2]['value']
			__EVENTVALIDATION = data_out[5]['value']
		except:
			quit()
		
		DATA = {
			'__EVENTTARGET':'ctl00$ContentPlaceHolder1$TabContainer1$TabPanel1$lbox_general',
			'__LASTFOCUS':'',
			'__VIEWSTATE': __VIEWSTATE,
			'__VIEWSTATEENCRYPTED':'',
			'__EVENTVALIDATION': __EVENTVALIDATION,
			'ctl00$ContentPlaceHolder1$TabContainer1$TabPanel1$ddl_class_edusys':'0',
			'ctl00$ContentPlaceHolder1$TabContainer1$TabPanel1$ddl_class_dept':'13',
			'ctl00$ContentPlaceHolder1$TabContainer1$TabPanel1$btn_queryclass':'查詢'
		}
		response = self.session.post(self.url, data = DATA)
		data = bs4.BeautifulSoup(response.text, "html.parser")
		data_out = data.find_all(type='hidden')

		try:
			if data_out[2]['value'] != '' and data_out[5]['value'] != '': 
				self.__VIEWSTATE = data_out[2]['value']
				self.__EVENTVALIDATION = data_out[5]['value']
			else:
				quit()
		except:
			quit()
		pass

if __name__ == '__main__':

	tStart = time.time()#計時結束

	classification = [	
						"人文藝術領域","人文經典類","藝術美學類","哲學思維類",
						"歷史文明類","社會科學領域","歷史文化類","法政與社會類",
						"商管經濟類","自然科學領域","科技與社會類","生命科學類",
						"實證與推理類","綜合實踐領域"
					 ]

	threads = []
	threadNum = len(classification)
	for count in range(threadNum):
		threads.append(catch_all_class_status(classification[count]))

	for count in range(threadNum):
		threads[count].start()
	
	for count in range(threadNum):
		threads[count].join()

	tEnd = time.time()#計時結束

	#列印結果
	print("It cost {0} sec".format(tEnd - tStart))
	print(tEnd - tStart)