import re
import sqlite3
import time
def add_log(info):
	f = open('log.txt','a')
	f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+'	'+info)
	f.write('\n')
	f.close()
	
def get_loc(story):
	location_items = []
	areaInfo = None
	try:
		areaInfo = story.find_element_by_class_name('areaInfo')
	except:
		None
	if areaInfo:
		pattern = re.compile(r'http.*?lat=(.*?)&amp;lng=(.*?)&amp;addr=(.*?)"', re.S)
		location_items = re.findall(pattern, areaInfo.get_attribute('innerHTML'))[0]
		print('位置：', location_items[2])
		print('经度：', location_items[0])
		print('纬度：', location_items[1])
		location = location_items[2]
		longitude = location_items[0]
		latitude = location_items[1]
	else:
		location = ""
		longitude = ""
		latitude = ""
	return location , longitude , latitude
	
def get_time(story):
	timel = story.find_elements_by_class_name('time')
	try:
		time=timel[1].get_attribute('title')
		qtime=timel[0].get_attribute('title')
	except:
		time=timel[0].get_attribute('title')
		qtime=""
	return time, qtime
	
def get_mood(self, story):
	mood = ""
	try:
		mood = self.browser.find_element_by_xpath('//*[@id="'+self.cid+'"]/div[3]/div[3]/div[1]/div/div/div[2]/div/div/div[1]/a[2]').text
		print('心情：'+mood)
		try:
			mood = self.browser.find_element_by_xpath('//*[@id="'+self.cid+'"]/div[3]/div[3]/div/div[2]/div[1]/div/div/div[2]/div/div/div[1]/a[2]text').text
			print('心情：'+mood)
		except:
			None
	except:
		None
	return mood
	
def get_quotation_html(self, story):
	try:
		quotation_block = story.find_element_by_class_name('noMSource')
		print(quotation_block.text)
		qauthor_valid = quotation_block.text
		qauthor = str("")
	except:
		qauthor = self.browser.find_element_by_xpath('//*[@id="'+self.cid+'"]/div[3]/div[4]/div/div[1]/strong/a[1]').get_attribute('title')
		try:
			#html分析
			qauthor_html = self.browser.find_element_by_xpath('//*[@id="'+self.cid+'"]/div[3]/div[4]/div/div[1]/div').get_attribute('innerHTML')#先得到HTML版本的信息
			qauthor_valid = ''.join(c for c in qauthor_html if ord(c) >= 32)#删除控制字符
			if qauthor_valid.startswith('<div>'):#去除掉最外层div标签
				qauthor_valid = qauthor_valid[5:]
			if qauthor_valid.endswith('</div>'):
				qauthor_valid = qauthor_valid[:-6]
			
			#处理qqemoji
			pattern_qqemo = re.compile(r'(<img.*?>)', re.S)#定义动作：找出所有img标签成一个组
			pattern_qqemo_img = re.compile(r'crs="(.*?)"', re.S)#定义动作：找出crs属性的内容（URL）
			pattern_qqemo_name = re.compile(r'title="(.*?)"', re.S)#定义动作：找出tittle属性的内容（URL）
			qqemos = re.findall(pattern_qqemo, qauthor_valid)#在qauthor_valid之pattern_qqemo，找出img
			for qqemo in qqemos:#循环组内所有项
				qqemo_url = re.findall(pattern_qqemo_img, qqemo)[0]#用pattern_qqemo_img得到url
				print("emoji:"+qqemo_url)
				try:
					qqemo_name = re.findall(pattern_qqemo_name, qqemo)[0]#用pattern_qqemo_img得到名字
				except:
					qqemo_name = ""
				if(qqemo_url[36:39] == 'emo'):
					qqemo_name = 'z'+qqemo_name
				qauthor_valid = qauthor_valid.replace(qqemo, '<emoji="' + qqemo_url + '">')#重新组合qauthor_valid
				if sql_emoji(self,qqemo_url):
					print('数据库中已存在这张emoji')
				else:
					self.c.execute("INSERT INTO EMOJI (NAME,URL) VALUES ('"+qqemo_name+"','"+qqemo_url+"')")
					print("INSERT INTO EMOJI (NAME,URL) VALUES ('"+qqemo_name+"','"+qqemo_url+"')")
					self.conn.commit()
			#处理话题
			pattern = re.compile(r'(<a href="http://k.t.qq.com.*?</a>)', re.S)
			topics = re.findall(pattern, qauthor_valid)
			for topic in topics:
				topic_word = topic.split('#')[1]
				qauthor_valid = qauthor_valid.replace(topic,  '#' + topic_word + '#')
			#处理at
			pattern_friend = re.compile(r'(<em rel=.*?</em>)', re.S)
			pattern_friend_name = re.compile(r'<em.*?title="(.*?)"', re.S)
			friends = re.findall(pattern_friend, qauthor_valid)
			for friend in friends:
				friend_name = re.findall(pattern_friend_name, friend)[0]
				qauthor_valid = qauthor_valid.replace(friend, "@" + friend_name)
			#处理链接
			pattern_url = re.compile(r'(<a.*?</a>)', re.S)
			pattern_url_str = re.compile(r'href="(.*?)"', re.S)
			urls = re.findall(pattern_url, qauthor_valid)
			for url in urls:
				url_str = re.findall(pattern_url_str, url)[0]
				qauthor_valid = qauthor_valid.replace(url,  url_str)
			print('原文作者：',qauthor)
			print('原文内容：',qauthor_valid)
		except:
			qauthor_valid = self.browser.find_element_by_xpath('//*[@id="'+self.cid+'"]/div[3]/div[4]/div/div[1]/div').text
			print('转发原文中有错误，可能是罕见的emoji，只能获取纯文本内容')
			add_log(self.cid+'转发原文中有错误，可能是罕见的emoji，只能获取纯文本内容')
	return qauthor , qauthor_valid
	
def get_image(self,story):
	URLs = []
	picBox = None
	imgGroup = None
	bgr = None
	rank = 0
	try:
		picBox = story.find_element_by_class_name('picBox')
	except:
		None
	try:
		imgGroup = story.find_element_by_class_name('tl_imgGroup')
	except:
		None
	try:
		bgr = story.find_element_by_class_name('bgr')
	except:
		 None
	try:
		picVote = story.find_element_by_class_name('tl_picVote_lst')
	except:
		None
	
	if picVote:#图片投票
		print('找到图片投票')
		try:
			self.browser.find_element_by_xpath('//*[@id="'+self.cid+'"]/div[3]/div[3]/div/div[2]/div[2]/div/a').click()
		except:
			None
		img_tags = picVote.find_elements_by_tag_name('img')
		for img_tag in img_tags:
			img_url = img_tag.get_attribute('src')
			if(img_url != 'http://mat1.gtimg.com/www/mb/img/pic_vote/icon_ok.png'):
				print('图片：', img_url[0:47])
				img_url=img_url[0:47]
				if sql_img(self,img_url):
					print('数据库中已存在这张图片')
				else:
					self.c.execute("INSERT INTO IMAGE (CID,RANK,URL) VALUES ("+self.cid+","+str(rank)+",'"+img_url+"')");
					rank+=1
					
	if picBox:#单图片
		print('找到单张图片')
		img_url = picBox.find_element_by_tag_name('a').get_attribute('href')
		print('图片：', img_url[0:47])
		img_url=img_url[0:47]
		if sql_img(self,img_url):
			print('数据库中已存在这张图片')
		else:
			self.c.execute("INSERT INTO FIMAGE (CID,RANK,URL) VALUES ("+self.cid+","+str(rank)+",'"+img_url+"')");
			rank+=1
	if bgr:#长图片
		try:
			print('找到长图')
			img_url = bgr.get_attribute('crs')
			print('图片：', img_url[0:47])
			img_url=img_url[0:47]
			if sql_img(self,img_url):
				print('数据库中已存在这张图片')
			else:
				self.c.execute("INSERT INTO FIMAGE (CID,RANK,URL) VALUES ("+self.cid+","+str(rank)+",'"+img_url+"')");
				rank+=1
		except:
			print('分析长图失败')
			add_log('分析长图失败：'+self.cid)
	if imgGroup:#多图片
		print('找到多图组')
		a_tags = imgGroup.find_elements_by_tag_name('a')
		for a_tag in a_tags:
			img_url = a_tag.get_attribute('href')
			print('图片：', img_url[0:47])
			img_url=img_url[0:47]
			if sql_img(self,img_url):
				print('数据库中已存在这张图片')
			else:
				self.c.execute("INSERT INTO FIMAGE (CID,RANK,URL) VALUES ("+self.cid+","+str(rank)+",'"+img_url+"')");
				rank+=1
	self.conn.commit()
	
def sql_img(self,img_url):
	flag=False#判断数据库中是否已存在
	self.excursor = self.c.execute("SELECT * FROM FIMAGE WHERE CID == '"+self.cid+"' AND URL == '"+img_url+"'")
	for row in self.excursor:
		flag=True
	return flag
	
def sql_qimg(self,img_url):
	flag=False#判断数据库中是否已存在
	self.excursor = self.c.execute("SELECT * FROM FIMAGE WHERE CID == '"+self.cid+"' AND URL == '"+img_url+"'")
	for row in self.excursor:
		flag=True
	return flag

def sql_emoji(self,img_url):
	flag=False#判断数据库中是否已存在
	self.excursor = self.c.execute("SELECT * FROM EMOJI WHERE URL == '"+img_url+"'")
	for row in self.excursor:
		flag=True
	return flag
	
def sql_insert(self):
	flag=False#判断数据库中是否已存在
	self.excursor = self.c.execute("SELECT * FROM FAVOR WHERE CID == " + self.cid)
	for row in self.excursor:
		flag=True
	if flag==False:
		try:
			self.c.execute("INSERT INTO FAVOR (CID,TID,TYPE,AUTHOR,CONTENT,TIME,QAUTHOR,QCONTENT,QTIME,MOOD,LOCATION,LONGITUDE,LATITUDE) VALUES ("+self.cid+","+self.tid+","+str(self.type)+",'"+self.author+"','"+self.content+"','"+self.time+"','"+self.qauthor+"','"+self.qcontent+"','"+self.qtime+"','"+self.mood+"','"+self.location+"','"+self.longitude+"','"+self.latitude+"')");#用''引
		except:
			try:
				print('原文中可能包含非法引号，尝试处理后重新插入')
				self.qcontent = re.sub("\"", r"\'", self.qcontent)
				self.content = re.sub("\"", r"\'", self.content)
				self.c.execute('INSERT INTO FAVOR (CID,TID,TYPE,AUTHOR,CONTENT,TIME,QAUTHOR,QCONTENT,QTIME,MOOD,LOCATION,LONGITUDE,LATITUDE) VALUES ('+self.cid+','+self.tid+','+str(self.type)+',"'+self.author+'","'+self.content+'","'+self.time+'","'+self.qauthor+'","'+self.qcontent+'","'+self.qtime+'","'+self.mood+'","'+self.location+'","'+self.longitude+'","'+self.latitude+'")');#用""引
			except:
				sql_error = 'INSERT INTO FAVOR (CID,TID,TYPE,AUTHOR,CONTENT,TIME,QAUTHOR,QCONTENT,QTIME,MOOD,LOCATION,LONGITUDE,LATITUDE) VALUES ('+self.cid+','+self.tid+','+str(self.type)+',"'+self.author+'","'+self.content+'","'+self.time+'","'+self.qauthor+'","'+self.qcontent+'","'+self.qtime+'","'+self.mood+'","'+self.location+'","'+self.longitude+'","'+self.latitude+'")'
				print(sql_error)
				f = open('sql_error.txt','a')
				f.write(sql_error)
				f.write('\n')
				f.close()
				print('抱歉，貌似依旧没能插入，这条语句已经被打印并保存出来供手工处理')
		self.conn.commit()
	else:
		print("数据库中已存在这条记录")

def analyze_video(self,story):
	video_items = []
	videoBox = None
	try:
		videoBox = story.find_element_by_class_name('videoBox')
	except:
		None
	if videoBox:
		try:
			pattern = re.compile(r'realurl="(.*?)".*?reltitle="(.*?)".*?<img.*?crs="(.*?)"', re.S)
			video_items = re.findall(pattern, videoBox.get_attribute('outerHTML'))[0]
			print('视频名称：', video_items[1])
			print('视频网址：', video_items[0])
			print('视频封面：', video_items[2])
			flag=False#判断数据库中是否已存在
			self.excursor = self.c.execute("SELECT * FROM VIDEO WHERE CID == " + self.cid)
			for row in self.excursor:
				flag=True
			if flag==False:
				try:
					self.c.execute("INSERT INTO VIDEO (CID,NAME,URL,COVER) VALUES ("+self.cid+",'"+video_items[1]+"','"+video_items[0]+"','"+video_items[2]+"')");
					self.conn.commit()
				except:
					print('数据库插入失败')
			else:
				print('数据库中已存在这个视频')
		except:
			print('视频分析失败！')
			add_log('分析视频失败：'+self.cid)
			
def analyse_content_html(self,story):
	try:
		#html分析
		content_html = story.find_element_by_class_name('msgCnt').get_attribute('innerHTML')#先得到HTML版本的信息
		content_valid = ''.join(c for c in content_html if ord(c) >= 32)#删除控制字符
		if content_valid.startswith('<div>'):#去除掉最外层div标签
			content_valid = content_valid[5:]
		if content_valid.endswith('</div>'):
			content_valid = content_valid[:-6]
		
		#处理qqemoji
		pattern_qqemo = re.compile(r'(<img.*?>)', re.S)#定义动作：找出所有img标签成一个组
		pattern_qqemo_img = re.compile(r'crs="(.*?)"', re.S)#定义动作：找出crs属性的内容（URL）
		pattern_qqemo_name = re.compile(r'title="(.*?)"', re.S)#定义动作：找出tittle属性的内容（URL）
		qqemos = re.findall(pattern_qqemo, content_valid)#在content_valid之pattern_qqemo，找出img
		for qqemo in qqemos:#循环组内所有项
			qqemo_url = re.findall(pattern_qqemo_img, qqemo)[0]#用pattern_qqemo_img得到url
			print("emoji:"+qqemo_url)
			try:
				qqemo_name = re.findall(pattern_qqemo_name, qqemo)[0]#用pattern_qqemo_img得到名字
			except:
				qqemo_name = ""
			if(qqemo_url[36:39] == 'emo'):
				qqemo_name = 'z'+qqemo_name
			content_valid = content_valid.replace(qqemo, '<emoji="' + qqemo_url + '">')#重新组合content_valid
			if sql_emoji(self,qqemo_url):
				print('数据库中已存在这张emoji')
			else:
				self.c.execute("INSERT INTO EMOJI (NAME,URL) VALUES ('"+qqemo_name+"','"+qqemo_url+"')")
				self.conn.commit()
			
		#处理话题
		pattern = re.compile(r'(<a href="http://k.t.qq.com.*?</a>)', re.S)
		topics = re.findall(pattern, content_valid)
		for topic in topics:
			topic_word = topic.split('#')[1]
			content_valid = content_valid.replace(topic,  '#' + topic_word + '#')
			
		#处理at
		pattern_friend = re.compile(r'(<em rel=.*?</em>)', re.S)
		pattern_friend_name = re.compile(r'<em.*?title="(.*?)"', re.S)
		friends = re.findall(pattern_friend, content_valid)
		for friend in friends:
			friend_name = re.findall(pattern_friend_name, friend)[0]
			content_valid = content_valid.replace(friend, "@" + friend_name)
		
		#处理链接
		pattern_url = re.compile(r'(<a.*?</a>)', re.S)
		pattern_url_str = re.compile(r'href="(.*?)"', re.S)
		urls = re.findall(pattern_url, content_valid)
		for url in urls:
			url_str = re.findall(pattern_url_str, url)[0]
			content_valid = content_valid.replace(url,  url_str)
		
		#处理转发插图
		pattern_qimg = re.compile(r'(<i.*?</i>)', re.S)
		pattern_qimg_str = re.compile(r'data-rpurl="(.*?)"', re.S)
		qimgs = re.findall(pattern_qimg, content_valid)
		for qimg in qimgs:
			qimg_url = re.findall(pattern_qimg_str, qimg)[0]
			content_valid = content_valid.replace(qimg, '<img="' + qimg_url + '">')
			print(content_valid)
			if sql_qimg(self,qimg_url):
				print('数据库中已存在这张转发插图')
			else:
				self.c.execute("INSERT INTO FIMAGE (CID,RANK,URL) VALUES ('','','"+qimg_url+"')");
				self.conn.commit()
	except:
		content_valid = story.find_element_by_class_name('msgCnt').text
		print('原文中有错误，可能是罕见的emoji，只能获取纯文本内容')
		add_log(self.cid+'原文中有错误，可能是罕见的emoji，只能获取纯文本内容')
	return content_valid

def get_pi(url):
	try:
		pattern = re.compile(r'p=(\d+)', re.S)
		pi = int(re.findall(pattern, url)[0])
	except:
		pi=0
	return pi
