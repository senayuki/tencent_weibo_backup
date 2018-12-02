import sqlite3
import util
import os
import time
import re
'''
inbox index!
'''

HTML_INDEX_MAIN='<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="utf-8">\n    <title>私信索引</title>\n    <link rel="stylesheet" href="css/PM.css" />\n</head>\n<body>\n<h1>\n    私信索引\n</h1>\n</br>\n'
HTML_INDEX_END='</br></body>\n</html>'
messagelist=[]
imglist={}
user_dict={}
def emojiInContent(content):
	pattern_emoji = re.compile(r'(<emoji=.*?>)', re.S)
	emoji_urls=re.findall(pattern_emoji, content)
	for emoji in emoji_urls:
		file_name=emoji[emoji.rfind("/")+1:-2]
		content=content.replace(emoji,'<img class"emoji" src="../emoji_images/'+file_name+'">')
	return content

def timeConvert(timestamp):#输入UTC时间戳，返回北京时间
	timestamp+=28800#加上8小时时间差
	time_local = time.localtime(timestamp)
	format_time = time.strftime("%Y/%m-%d+ %H:%M:%S", time_local)
	format_time = format_time.replace("/","年")
	format_time = format_time.replace("-","月")
	format_time = format_time.replace("+","日")
	return format_time
def get_username(inbox_list):#传入ID列表
	for inbox in inbox_list:
		user_dict[inbox[0]]=inbox[0]	
	message_sql=c.execute("SELECT * FROM PM")
	for message in message_sql:
		messagelist.append(message)
	for message in messagelist:
		if(message[3]!="我"):
			user_dict[message[2]]=message[3]		
def build_index():#构建私信索引
	a_list=[]
	a_string='\n'
	for user in user_dict.keys():
		a_tag='<li><a href="pm/'+user+'.html">'+user_dict[user]+'</a></li>'
		a_list.append(a_tag)
	for a in a_list:
		a_string+="    "+a+"\n"
	with open("pm_index.html","w",encoding="utf-8") as f:
		f.write(HTML_INDEX_MAIN+a_string+HTML_INDEX_END)
def build_user_html():
	def takeTimeSort(list):#返回时间戳用于排序
		return list[1]
	def getImage(CID):#传入CID，查找对应图片，如果存在返回img标签，不存在则返回空字符串
		img_tag=""
		img_sql=c.execute("SELECT URL FROM PMIMAGE WHERE CID='"+str(message[0])+"'")#查找这条私信是否附有图片
		try:
			for img in img_sql:
				url=img[0]
				name=url[url.rfind("/")+1:]#处理链接
				if name in imglist.keys():
					name="../images/PM_images/"+name+imglist[name]#得到完整文件名

					img_tag='<img class="image" src="'+name+'" height="200">\n'
		except:
			None
		return img_tag
	for userid in user_dict.keys():#遍历用户
		user_dial=[]#存储与用户的对话
		for message in messagelist:#遍历列表中所有的信息
			if message[2]==userid:#如果筛选与此用户的记录
				user_dial.append(message)
		user_dial.sort(key=takeTimeSort,reverse=False)#按照时间正序排列，旧的在上新的在下

		build_html=[]#存储HTML条目
		for message in user_dial:#处理获取到的对话列表，逐条转换为HTML项目
			message_class="received_box"#判断收发消息，使用不同的class名称
			if(message[3]=="我"):#如果信息发送者是”我“
				message_class="sended_box"
			build_li='</br><div class="msgBox '+message_class+'"><div class="username">'+message[3]+'</div><div class="content">'+emojiInContent(message[4])+'</div><div class="time">'+timeConvert(message[1])+'</div>'+getImage(message[0])+'</div></div>'
			build_html.append(build_li)
		HTML_MAIN='<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="utf-8">\n    <title>私信:'+user_dict[userid]+'</title>\n    <link rel="stylesheet" href="../css/PM.css" />\n</head>\n<body>\n<h1>\n    私信:'+user_dict[userid]+'\n</h1>\n'
		HTML=HTML_MAIN.replace("私信列表","私信："+user_dict[userid])
		for li in build_html:
			HTML+=li+"\n"
		with open("PM\\"+userid+".html","w",encoding="utf-8") as f:
			f.write(HTML+HTML_INDEX_END)


uname = input("请输入用户ID：@")
print ("你输入的用户ID是: " + uname)
util.add_log('用户名是'+uname)
if (os.path.exists(uname+'.db')):
	conn = sqlite3.connect(uname+'.db')
	c = conn.cursor()
	print('打开数据库成功')
	util.add_log('打开数据库成功')
else:
	print('未能找到数据库')
	util.add_log('未能找到数据库')
	exit()
	
userlist_full = c.execute("SELECT DIAL FROM PM GROUP BY DIAL")#从PM列表筛选所有对话
util.add_log('开始构建私信索引页,读取用户列表')

for file in os.listdir(os.getcwd()+"\\images\\PM_images"):#构建img扩展名对照表
    name=os.path.splitext(file)[0]
    ext=os.path.splitext(file)[1]
    imglist[name]=ext
if not os.path.isdir("PM"):
	os.mkdir("PM")
get_username(userlist_full)#构建userlist
build_index()
build_user_html()
util.add_log('构建完毕')