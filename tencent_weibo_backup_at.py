# -*- coding: utf-8 -*-

from time import sleep
from selenium import webdriver
import sqlite3
import re
import util_at
import os

class tencent_weibo:
	def __init__(self):
		util_at.add_log('at备份启动')
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
		except:
			print('可能没有安装Firefox，请安装')
			exit()
	
	def login(self):
		print('开始登录腾讯微博...')
		url = 'http://t.qq.com/' + self.uname
		print('试图打开' + url)
		self.browser.get(url)
		sleep(3)
		if self.isElementExist(".map_404"):
			print('ID不存在！')
			util_at.add_log('网页发生404错误，退出')
			exit()
		else:
			try:
				try:
					self.browser.find_element_by_class_name('nologin_loginbtn').click()
					sleep(3)
				except:
					None
				try:
					self.browser.switch_to.frame('QuickLoginFrame')
					self.browser.switch_to.frame('login_div')
					self.browser.find_element_by_class_name('face').click()
					print('登录完毕')
					util_at.add_log('成功登陆')
					sleep(3)
					if self.isElementExist("face"):
						print('可能发生了自动登陆异常？')
					self.browser.set_page_load_timeout(5)
				except:
					print('登录可能失败了？找不到登陆按钮！')
				try:
					self.conn = sqlite3.connect(self.uname+'.db')
					print('打开数据库成功')
				except:
					print('打开数据库失败')
					os._exit(1)
				try:
					#CLASS TEXT NOT NULL,
					self.c = self.conn.cursor()
					self.c.execute('''CREATE TABLE AT
						   (CID INT NOT NULL,
						   TID INT NOT NULL,
						   TYPE INT NOT NULL,
						   AUTHOR TEXT NOT NULL,
						   CONTENT TEXT NOT NULL,
						   TIME TEXT NOT NULL,
						   QAUTHOR TEXT NOT NULL,
						   QCONTENT TEXT NOT NULL,
						   QTIME TEXT NOT NULL,
						   MOOD TEXT NOT NULL,
						   LOCATION TEXT NOT NULL,
						   LONGITUDE TEXT NOT NULL,
						   LATITUDE TEXT NOT NULL);''')
					self.conn.commit()
					self.c.execute('''CREATE TABLE IMAGE
						   (CID INT NOT NULL,
						   RANK INT NOT NULL,
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
					self.c.execute('''CREATE TABLE VIDEO
						   (CID INT NOT NULL,
						   NAME TEXT NOT NULL,
						   URL TEXT NOT NULL,
						   COVER TEXT NOT NULL);''')
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
				try:
					current_url = self.browser.current_url
					self.browser.switch_to.default_content()
					latest_url = self.c.execute("SELECT * FROM INFO WHERE ITEM=='LATEST_URL'")
					for row in latest_url:
						if row[1]!="":
							print("找到上次备份的URL：", row[1])
							util_at.add_log('找到上次的URL：' + row[1])
							start_url = row[1]
							tmp = input('请选择是否使用：0.使用 1.不使用\n')
							if(tmp!="0"):
								self.browser.get('http://t.qq.com/at?')
							else:
								
								latest_index = self.c.execute("SELECT * FROM INFO WHERE ITEM=='LATEST_INDEX'")
								for row in latest_index:
									self.page_index = int(row[1])
									print("上次的页数：", row[1])
								self.browser.get(start_url)
						else:
							try:
								self.browser.get('http://t.qq.com/at?#filter=0&id=342195102119035&pi=7&time=1401279495')
							except:
								None
				except:
					None
					self.conn.commit()
			except:
				print('登陆失败！网络不够顺畅？')
				os._exit(1)
	
	def get_stories(self):
		try:
			talk_list = self.browser.find_element_by_id('talkList')
			self.stories = talk_list.find_elements_by_tag_name('li') 
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
	
	def get_items(self):
		for story in self.stories:
			#类型判断，1原创2转播3评论4对话5视频6音乐9心情12赞
			self.type=1
			try:
				isquotation = story.find_element_by_class_name('replyBox')
				self.type=2
			except:
				None
			try:
				isComm = story.find_element_by_class_name('feedComm')
				self.type=3
			except:
				None
			try:
				isComm = story.find_element_by_class_name('feedLike')
				self.type=12
				continue
			except:
				None
			self.cid = story.get_attribute("id")
			self.tid = story.get_attribute("rel")
			try:
				self.author = story.find_element_by_class_name('userName').find_element_by_tag_name('a').get_attribute('title')
			except:
				print('出现灵异事件？')
				print('----------------------------------------------------------------------------------')
				util_at.add_log('出现灵异事件'+self.cid)
				continue
			self.content = util_at.analyse_content_html(self,story)
			if (self.content == '')and(self.author == '(@)'):
				util_at.add_log('找到一条原文已删除的收藏：'+self.cid)
				continue
			else:
				self.time, self.qtime = util_at.get_time(story)
				
				#打印信息
				print('CID：', self.cid)
				print('TID：', self.tid)
				if self.type == 1:
					print('类型：原创')
				else:
					if self.type == 2:
						print('类型：转播')
					else:
						if self.type == 3:
							print('类型：评论')
						else:
							if self.type == 12:
								continue
				print('作者：', self.author)
				print('内容：', self.content)
				print('时间：', self.time)
				#心情模块
				self.mood = util_at.get_mood(self, story)
				#视频模块
				util_at.analyze_video(self,story)
				if self.type!=1:#转评作者内容时间
					try:
						self.qauthor , self.qcontent = util_at.get_quotation_html(self,story)
					except:
						self.qauthor = ''
						self.qcontent = ''
					if self.qtime !="":
						print('原文时间：', self.qtime)
				else:
					self.qauthor = ""
					self.qcontent = ""
				util_at.get_image(self,story)
				self.location , self.longitude , self.latitude = util_at.get_loc(story)#定位
				util_at.sql_insert(self)
				print('----------------------------------------------------------------------------------')
	
	def start(self):
		while self.have_next_page:
			sleep(3)
			print('\n本页地址为：%s' % self.browser.current_url)
			if self.last_url != self.browser.current_url:
				self.last_url = self.browser.current_url
				print('开始分析腾讯微博第 %s 页...' % self.page_index)
				self.c.execute("UPDATE INFO set VALUE = '"+self.browser.current_url+"' where ITEM=='LATEST_URL'")
				self.c.execute("UPDATE INFO set VALUE = '"+str(self.page_index)+"' where ITEM=='LATEST_INDEX'")
				self.conn.commit()
				util_at.add_log('开始分析URL：'+self.browser.current_url+' 这是分析的第'+str(self.page_index)+'页')
				self.page_index += 1
				print('----------------------------------------------------------------------------------')
				self.get_stories()
				self.get_items()
			else:
				print('与上页面重复，直接进入下一页')
				util_at.add_log('发生一次页面重复'+self.browser.current_url)
				try:
					print('试图刷新解决')
					util_at.add_log('试图刷新解决')
					self.browser.refresh()
					sleep(3)
				except:
					sleep(3)
			self.click_next_page()

			sleep(1)
		else:
			if (self.page_index-1) % 100 == 0:
				try:
					print('\n一个百页达成！\n请耐心等待几秒，正在平缓进入下一个百页。')
					self.browser.get('http://t.qq.com/at?#filter=0?pi=1&id='+self.cid+'&time='+self.tid)
					self.browser.refresh()
				except:
					try:
						self.browser.refresh()
					except:
						None
				self.have_next_page = True
				sleep(3)
				self.start()
			else:
				self.c.execute("UPDATE INFO set VALUE = '' where ITEM=='LATEST_URL'")
				self.c.execute("UPDATE INFO set VALUE = '' where ITEM=='LATEST_INDEX'")
				self.c.execute("UPDATE INFO set VALUE = '' where ITEM=='LATEST_MODE'")
				self.conn.commit()
				print('备份完成，本次共计备份'+str(self.page_index-1)+'页。')
				util_at.add_log('备份完成，本次共计备份'+str(self.page_index-1)+'页。')

	def isElementExist(self,element):
	#确认元素是否存在，如果存在返回true，不存在返回false
		flag=True
		try:
			weibo.browser.find_element_by_css_selector(element)
			return flag
		except:
			flag=False
			return flag
weibo = tencent_weibo()
weibo.login()
weibo.start()