# -*- coding: utf-8 -*-

import time
from time import sleep
from selenium import webdriver
import sqlite3
import re
import os
import util_at
class tencent_weibo:
	def sql_emoji(self,img_url):
		flag=False#判断数据库中是否已存在
		self.excursor = self.c.execute("SELECT * FROM EMOJI WHERE URL == '"+img_url+"'")
		for row in self.excursor:
			flag=True
		return flag

	def sql_img(self,img_url):
		flag=False#判断数据库中是否已存在
		self.excursor = self.c.execute("SELECT * FROM PMIMAGE WHERE CID == '"+self.cid+"' AND URL == '"+img_url+"'")
		for row in self.excursor:
			flag=True
		return flag

	def __init__(self):
		util_at.add_log('PM备份启动')
		self.uname = input("请输入用户ID：@")
		print ("你输入的用户ID是: " + self.uname)
		util_at.add_log('用户名是'+self.uname)
		self.page_index = 1
		self.have_next_page = True
		self.next_page_url = None
		self.stories = None
		self.last_url = None
		try:
			self.browser = webdriver.Firefox()
			None
		except:
			print('可能没有安装Firefox，请安装')
			exit()
	
	def open_db(self):
		try:
			self.conn = sqlite3.connect(self.uname+'.db')
			print('打开数据库成功')
		except:
			print('打开数据库失败')
			os._exit(1)
		try:
			self.c = self.conn.cursor()
			self.c.execute('''CREATE TABLE PM
				   (CID INT NOT NULL,
				   TID INT NOT NULL,
				   DIAL TEXT NOT NULL,
				   AUTHOR TEXT NOT NULL,
				   CONTENT TEXT NOT NULL,
				   TIME TEXT NOT NULL);''')
			self.c.execute('''CREATE TABLE PMT
				   (AUTHOR TEXT NOT NULL);''')
			self.conn.commit()
			self.c.execute('''CREATE TABLE PMIMAGE
				   (CID INT NOT NULL,
				   URL TEXT NOT NULL);''')
			self.conn.commit()
			self.c.execute('''CREATE TABLE INFO
				   (ITEM TEXT NOT NULL,
				   VALUE TEXT NOT NULL);''')
			self.conn.commit()
			self.c.execute('''CREATE TABLE EMOJI
				   (NAME TEXT NOT NULL,
				   URL TEXT NOT NULL);''')
			self.conn.commit()
			self.c.execute("INSERT INTO INFO (ITEM,VALUE) VALUES ('LATEST_URL','');");
			self.c.execute("INSERT INTO INFO (ITEM,VALUE) VALUES ('LATEST_MODE','');");
			self.c.execute("INSERT INTO INFO (ITEM,VALUE) VALUES ('LATEST_INDEX','');");
			self.c.execute("INSERT INTO INFO (ITEM,VALUE) VALUES ('LATEST_USER','');");
			self.conn.commit()
			print('创建表成功')
			util_at.add_log('创建库成功')
		except:
			print('找到旧表')
			util_at.add_log('找到旧数据库')
			flag=False#判断数据库中是否已存在
			self.excursor = self.c.execute("SELECT * FROM INFO WHERE ITEM == 'LATEST_USER'")
			for row in self.excursor:
				flag=True
			if flag == False:
				self.c.execute("INSERT INTO INFO (ITEM,VALUE) VALUES ('LATEST_USER','');");
				self.conn.commit()
	
	def login(self):
		self.open_db()
		print('开始登录')
		url = 'http://t.qq.com/'+self.uname
		self.browser.get(url)
		sleep(3)
		try:
			self.browser.switch_to.frame('QuickLoginFrame')
			self.browser.switch_to.frame('login_div')
			self.browser.find_element_by_class_name('face').click()

			print('登录完毕')
		except:
			print('登录超时')
		self.browser.set_page_load_timeout(10)
		try:
			self.browser.switch_to.default_content()
			self.browser.get('http://t.qq.com/messages/inbox')
			sleep(10)
			print('打开私信页面')
		except:
			None
	
	def get_stories(self):
		try:
			user_lists = self.browser.find_element_by_id('wbpmlistitems')
			self.stories = user_lists.find_elements_by_tag_name('div') 
		except:
			None
	
	def click_next_page(self):
		pageNav = self.browser.find_element_by_id('pageNav')
		try:
			next_page = pageNav.find_element_by_link_text(u'下一页')
		except:
			self.have_next_page = False
		try:
			self.next_page_url = next_page.get_attribute('href')
			if self.next_page_url:
				next_page.click()
			else:
				None
		except:
			None

	def get_userid(self):
		flag=True#判断数据库中是否已存在
		for story in self.stories:
			if (story.get_attribute("tid") != None) and (story.get_attribute("tid") != ''):
				temp = story.get_attribute("tid")
				print('找到ID:' +temp)
				self.excursor = self.c.execute("SELECT * FROM PMT WHERE AUTHOR == '"+temp+"'")
				for row in self.excursor:
					flag=False
				if flag:
					self.c.execute("INSERT INTO PMT (AUTHOR) VALUES ('"+temp+"')");
					self.conn.commit()
					print('已插入')
				else:
					print('数据库中已存在')
	
	def get_users(self):
		while self.have_next_page:
			sleep(3)
			util_at.add_log('开始分析URL：'+self.browser.current_url+' 这是分析的第'+str(self.page_index)+'页')
			self.page_index += 1
			print('----------------------------------------------------------------------------------')
			self.get_stories()
			self.get_userid()
			self.click_next_page()
			sleep(1)
		else:
			print('ID获取完成，本次共计爬取'+str(self.page_index-1)+'页。')
			util_at.add_log('ID获取完成，本次爬取'+str(self.page_index-1)+'页。')

	def get_item(self,userID):
		more_flag = False
		try:
			self.browser.switch_to.default_content()
			self.browser.get('http://t.qq.com/messages/inbox#pmtid='+userID)
			sleep(5)
			print('打开页面')
			self.browser.refresh()
			sleep(3)
		except:
			None
			
		try:#1无限循环翻找'更多'
			while(1):
				self.browser.find_element_by_xpath('//*[@id="wbpmrecordmore"]/a').click()
				more_flag = True
				sleep(3)
		except:
			None
			
		try:#2无限循环翻找'更多'
			while(1):
				self.browser.find_element_by_xpath('//*[@id="wbpmrecordmore"]/a').click()
				more_flag = True
				sleep(3)
		except:
			None
			
		try:#获取list
			pm_list = self.browser.find_element_by_id('wbpmrecorditems')
			self.stories = pm_list.find_elements_by_class_name('wbpmunit')
		except:
			None
		for story in self.stories:
			self.cid = story.get_attribute("tid")
			self.tid = story.get_attribute("tm")
			time = self.browser.find_element_by_xpath('//*[@id="wbpmrecord'+self.cid+'"]/div[6]/span').text
			try:
				author = story.find_element_by_class_name('icon').find_element_by_tag_name('a').get_attribute('title')
			except:
				author = '我'
			print('CID:'+self.cid)
			print('TID:'+self.tid)
			print('作者:'+author)
			print('时间:'+time)
			con = self.browser.find_element_by_xpath('//*[@id="wbpmrecord'+self.cid+'"]/div[5]/div[2]').get_attribute('innerHTML')
			if con.startswith('<div>'):#去除掉最外层div标签
				con = con[5:]
			if con.endswith('</div>'):
				con = con[:-6]

			#处理qqemoji
			pattern_qqemo = re.compile(r'(<img.*?>)', re.S)#定义动作：找出所有img标签成一个组
			pattern_qqemo_img = re.compile(r'crs="(.*?)"', re.S)#定义动作：找出crs属性的内容（URL）
			pattern_qqemo_name = re.compile(r'title="(.*?)"', re.S)#定义动作：找出tittle属性的内容（URL）
			qqemos = re.findall(pattern_qqemo, con)#在con之pattern_qqemo，找出img
			for qqemo in qqemos:#循环组内所有项
				qqemo_url = re.findall(pattern_qqemo_img, qqemo)[0]#用pattern_qqemo_img得到url
				print("emoji:"+qqemo_url)
				try:
					qqemo_name = re.findall(pattern_qqemo_name, qqemo)[0]#用pattern_qqemo_img得到名字
				except:
					qqemo_name = ""
				if(qqemo_url[36:39] == 'emo'):
					qqemo_name = 'z'+qqemo_name
				con = con.replace(qqemo, '<emoji="' + qqemo_url + '">')#重新组合con
				if self.sql_emoji(qqemo_url):
					print('数据库中已存在这张emoji')
				else:
					self.c.execute("INSERT INTO EMOJI (NAME,URL) VALUES ('"+qqemo_name+"','"+qqemo_url+"')")
					print("INSERT INTO EMOJI (NAME,URL) VALUES ('"+qqemo_name+"','"+qqemo_url+"')")
					self.conn.commit()
			#处理话题
			pattern = re.compile(r'(<a href="http://k.t.qq.com.*?</a>)', re.S)
			topics = re.findall(pattern, con)
			for topic in topics:
				topic_word = topic.split('#')[1]
				con = con.replace(topic,  '#' + topic_word + '#')
			#处理at
			pattern_friend = re.compile(r'(<em rel=.*?</em>)', re.S)
			pattern_friend_name = re.compile(r'<em.*?title="(.*?)"', re.S)
			friends = re.findall(pattern_friend, con)
			for friend in friends:
				friend_name = re.findall(pattern_friend_name, friend)[0]
				con = con.replace(friend, "@" + friend_name)
			#处理链接
			pattern_url = re.compile(r'(<a.*?</a>)', re.S)
			pattern_url_str = re.compile(r'href="(.*?)"', re.S)
			urls = re.findall(pattern_url, con)
			for url in urls:
				url_str = re.findall(pattern_url_str, url)[0]
				con = con.replace(url,  url_str)
			print('内容：', con)
			#处理图片
			try:
				img_url = self.browser.find_element_by_xpath('//*[@id="wbpmrecord'+self.cid+'"]/div[5]/div[3]/a').get_attribute('href')
				print('找到图片')
				print('图片：', img_url[0:47])
				img_url=img_url[0:47]
				if self.sql_img(img_url):
					print('数据库中已存在这张图片')
				else:
					self.c.execute("INSERT INTO PMIMAGE (CID,URL) VALUES ("+self.cid+",'"+img_url+"')");
					self.conn.commit()
			except:
				None
			#加入数据库
			flag=False
			self.excursor = self.c.execute("SELECT * FROM PM WHERE CID == " + self.cid)
			for row in self.excursor:
				flag=True
			if flag==False:
				try:
					self.c.execute(u"INSERT INTO PM (CID,TID,DIAL,AUTHOR,CONTENT,TIME) VALUES ("+self.cid+","+self.tid+",'"+userID+"','"+author+"','"+con+"','"+time+"')");#用''引
				except:
					try:
						print('原文中可能包含非法引号，尝试处理后重新插入')
						con = re.sub("\"", r"\'", self.con)
						self.c.execute(u'INSERT INTO PM (CID,TID,DIAL,AUTHOR,CONTENT,TIME) VALUES ('+self.cid+','+self.tid+',"'+userID+'","'+author+'","'+con+'","'+time+'")');#用""引
					except:
						sql_error = u'INSERT INTO PM (CID,TID,DIAL,AUTHOR,CONTENT,TIME) VALUES ('+self.cid+','+self.tid+',"'+userID+'","'+author+'","'+con+'","'+time+'")'
						print(sql_error)
						f = open('sql_error.txt','a')
						f.write(sql_error)
						f.write('\n')
						f.close()
						print('抱歉，貌似依旧没能插入，这条语句已经被打印并保存出来供手工处理')
				self.conn.commit()
			else:
				print("数据库中已存在这条记录")
			self.c.execute("UPDATE INFO set VALUE = '"+userID+"' where ITEM=='LATEST_USER'")
			self.conn.commit()
			print('----------------------------------------------------------------------------------')
		sleep(1)

	def start(self):
		self.open_db()
		#寻找start_user
		latest_user = self.c.execute("SELECT * FROM INFO WHERE ITEM=='LATEST_USER'")
		for row in latest_user:
			if(row[1]==''):
				print('没有找到进度')
				self.get_users()
				user_list = self.c.execute("SELECT DISTINCT AUTHOR FROM PMT")
				for user in user_list:
					start_user = user[0]
					break
			else:
				print("找到上次备份的进度，用户名：", row[1])
				tmp = input('请选择是否使用：0.使用 1.不使用\n')
				if(tmp!="0"):#不使用
					user_list = self.c.execute("SELECT DISTINCT AUTHOR FROM PMT")
					for user in user_list:
						start_user = user[0]
						break
				else:#使用
					start_user = row[1]
					user_list = self.c.execute("SELECT DISTINCT AUTHOR FROM PMT")
			break
		print()
		user_list = self.c.execute("SELECT DISTINCT AUTHOR FROM PMT")
		start_flag=False
		got_list = []
		for user in user_list:
			if user[0] == start_user:
				start_flag=True
			if start_flag == True:#此时找到记录的ID，可以开始抓取了
				got_list.append(user[0])
		for userID in got_list:
			print()
			print('开始抓取ID：'+userID)
			self.get_item(userID)
			print(userID+'抓取完毕')
			sleep(3)

weibo = tencent_weibo()
user_list = []
start_user = ''
weibo.login()
weibo.start()