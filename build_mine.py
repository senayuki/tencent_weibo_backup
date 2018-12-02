import os
import sqlite3
import re
import time
from bs4 import BeautifulSoup
CUT=3000#设置分页数量
img_file_dict={}
img_info_dict={}
video_info_dict={}
cont_info_dict={}
TYPEDICT={1:"原创",2:"转播",3:"评论",12:"赞"}
MOODDICT={
	"狂喜":["浮生苦短，必须性感。","01_50"],
	"偷乐":["今天很欢乐，好心情要保鲜。","02_50"],
	"无感":["今日无悲喜，平平淡淡才是真。","03_50"],
	"伤心":["开心了就笑，不开心了就过会再笑。","04_50"],
	"咆哮":["郁闷至极，人生没有一帆风顺。","05_50"],
	"幸福":["#光棍节求桃花#恋爱ING，愿这朵桃花越开越好","Valentine_day_01_50"],
	"憧憬":["#光棍节求桃花#今年光棍节种下对桃花的期待，等待明年桃花开","Valentine_day_02_50"],
	"淡定":["#光棍节求桃花#年年岁岁花相似，笑看你们织毛衣","Valentine_day_03_50"],
	"孤单":["#光棍节求桃花#空虚寂寞冷，求桃花傍身","Valentine_day_04_50"],
	"心痛":["#光棍节求桃花#我的桃花啊，你在哪里？","Valentine_day_05_50"],
	}
def timeConvert(timestamp):#输入UTC时间戳，返回北京时间 xxxx年xx月xx日 xx:xx:xx
	timestamp+=28800#加上8小时时间差
	time_local = time.localtime(timestamp)
	format_time = time.strftime("%Y/%m-%d+ %H:%M:%S", time_local)
	format_time = format_time.replace("/","年")
	format_time = format_time.replace("-","月")
	format_time = format_time.replace("+","日")
	return format_time
def build_ext_dict(dir,dict):#输入空字典，构建文件名扩展名对照 dict[文件名,.扩展名]
	for file in os.listdir(os.getcwd()+"\\"+dir):
		name=os.path.splitext(file)[0]
		ext=os.path.splitext(file)[1]
		dict[name]=ext
def getTag_location(location,longitdue,latitude):#三个参数传入 位置信息，经度，纬度
	location_tag=""
	if (location=="" and longitdue=="" and latitude==""):#如果不全为空，则说明存在定位
		return location_tag
	else:
		#Google地图经纬度API：https://www.google.com/maps/search/?api=1&query=纬度,经度
		location_tag='<div class="location"><a href="https://www.google.com/maps/search/?api=1&query='+latitude+','+longitdue+'" target="_blank">'+location+'</a></div>\n'
		return location_tag
def getTag_moodBox(mkey):
	mood_tag=""
	if mkey!="":#如果有心情
		mood_tag='<div class="moodBox"><div class="moodpic"><div><img height="50%" width="50%" src="../css/mood/'+MOODDICT[mkey][1]+'.gif"></div><div>'+mkey+'</div></div><div class="moodcnt">'+MOODDICT[mkey][0]+'</div></div></br>\n'
	return mood_tag
def getTag_videoBox(CID):
	video_tag=""
	if CID in video_info_dict.keys():#如果有视频
		dict=video_info_dict[CID]
		video_tag='<div class="videoBox"><div class="videoItem"><a title="'+dict["TITLE"]+'" href="'+dict["URL"]+'" target="_blank"><img src="'+dict["COVER"]+'"></a></div></div>\n'
	return video_tag
def getTag_picBox(dir,img_file_dict,CID):#根据CID构建
	#传入CID，数据库查IMAGE找对应图片，如果存在返回img标签，不存在则返回空字符串
	img_tag=""
	if CID in img_info_dict.keys():#如果包含图片，否则不返回picBox
		dict=img_info_dict[CID]
		for img in sorted(dict.keys()):#img是一个int类型的index
			url=dict[img]
			name=url[url.rfind("/")+1:]#处理链接
			if name in img_file_dict.keys():
				name="../"+dir+"/"+name+img_file_dict[name]#得到完整文件名
				img_tag=img_tag+'    <div class="imgItem"> <img class="image" src="'+name+'"> </div>\n'
		img_tag='<div class="picBox">\n'+img_tag+'</div>\n'
	else:
		None
	return img_tag

def emojiInContent(content):#处理正文的emoji
	pattern_emoji = re.compile(r'(<emoji=.*?>)', re.S)
	emoji_urls=re.findall(pattern_emoji, content)
	for emoji in emoji_urls:
		file_name=emoji[emoji.rfind("/")+1:-2]
		content=content.replace(emoji,'<img class"emoji" src="../images/emoji_images/'+file_name+'">')
	return content

def imgInContent(dir,dict,content):#图片文件夹 扩展名字典 正文 处理正文中的图片链接
	pattern_img = re.compile(r'(<img=.*?>)', re.S)
	img_urls=re.findall(pattern_img, content)
	for img in img_urls:
		file_name=img[img.rfind("/")+1:-2]
		file_name=file_name+dict[file_name]#需要添加查找图片判断扩展名并添加，因为img本来就不带扩展名
		content=content.replace(img,'<a class"imgInContent" href="../'+dir+'/'+file_name+'" target="_Blank"><i>图片</i></a>')
	return content

def build_msgBox(CID):
	#存为新的变量以节省一层查询
	msg_dict=cont_info_dict[CID]
	msgtype=cont_info_dict[CID]["TYPE"]
	#如果转评相关信息全部为空，则不是一个转评
	isReply=True
	if(msg_dict["QAUTHOR"]=="" and msg_dict["QCONTENT"]=="" and msg_dict["QTIME"]==""):
		isReply=False

	#msgBox前标签
	#本文用户名与类型
	username='<div class="userName">'+msg_dict["AUTHOR"]+'<span class="type">'+TYPEDICT[msgtype]+'</span></div>\n'
	#本文正文
	content=imgInContent(IMG_DIR,img_file_dict,emojiInContent(msg_dict["CONTENT"]))
	content='<div class="msgCnt">'+content+'</div>\n'
	#获取图片
	picbox=getTag_picBox(IMG_DIR,img_file_dict,CID)
	#获取视频
	videobox=getTag_videoBox(CID)
	#获取心情
	moodbox=getTag_moodBox(msg_dict["MOOD"])
	#获取定位
	locationbox=getTag_location(msg_dict["LOCATION"],msg_dict["LONGITUDE"],msg_dict["LATITUDE"])
	#本文时间
	strtime=timeConvert(msg_dict["TID"])
	time='<div class="time">'+strtime+'</div>\n'
	if isReply:#如果是转评
		#处理转评特有内容
		qusername='<div class="QuserName">'+msg_dict["QAUTHOR"]+'</div>'
		qcontent=imgInContent(IMG_DIR,img_file_dict,emojiInContent(msg_dict["QCONTENT"]))
		qcontent='<div class="replyCnt">'+qcontent+'</div>\n'
		qtime='<div class="time">'+msg_dict["QTIME"]+'</div>\n'
		#构建HTML
		msg='<div class="msgBox">\n'+username+content+'<div class="replyBox">\n'+qusername+qcontent+picbox+videobox+moodbox+locationbox+qtime+'</div>\n'+time+'</div></br>\n'
	else:
		msg='<div class="msgBox">\n' + username + content + picbox + videobox + moodbox + locationbox + time + '</div></br>\n'
	return msg,strtime[:11]#strtime为日期，用于分页时的命名

def build_video_dict(c):#video_info_dict[CID]{字典} 由于只有一个表存储VIDEO，且不下载视频图片，所以无需参数
	sql_list=c.execute("SELECT * FROM VIDEO")
	for video in sql_list:
		video_info_dict[video[0]]={"TITLE":video[1],"URL":video[2],"COVER":video[3]}

def build_img_dict(c,img_table,img_info_dict):#img_info_dict[CID][img_index]=URL
	sql_list=c.execute("SELECT * FROM "+img_table)
	for img in sql_list:
		if img[0] not in img_info_dict.keys():#如果不存在这个
			img_info_dict[img[0]]={}
		img_info_dict[img[0]][img[1]]=img[2]

def build_content_list(c,content_table,cont_info_dict):#cont_info_dict[CID]{字典}
	sql_list=c.execute("SELECT * FROM "+content_table+" ORDER BY TID")
	for content in sql_list:
		###数据库中居然把经度和纬度写反了？？？？此处输入到词典时修正了问题
		cont_info_dict[content[0]]={"TID":content[1],"TYPE":content[2],"AUTHOR":content[3],"CONTENT":content[4],"TIME":content[5],"QAUTHOR":content[6],"QCONTENT":content[7],"QTIME":content[8],"MOOD":content[9],"LOCATION":content[10],"LATITUDE":content[11],"LONGITUDE":content[12]}

def openSQLite(uname):
	if (os.path.exists(uname+'.db')):
		conn = sqlite3.connect(uname+'.db')
		c = conn.cursor()
		print('打开数据库成功')
	else:
		print('未能找到数据库')
		exit()
	return c
def export_html(start,end,msgBoxes,con_type):
	timer=time.perf_counter()
	HTML_HEAD='<!DOCTYPE html><html><head><meta charset="UTF-8"><title></title><link rel="stylesheet" href="../css/MINE.css" /></head><body>\n'
	HTML_END='\n</body></html>'
	html=""
	for msg in msgBoxes:
		html+=msg
	html=HTML_HEAD+html+HTML_END
	soup_timer=time.perf_counter()
	soup = BeautifulSoup(html,"html.parser")#格式化HTML，耗时较长
	print("bs4 HTML读入用时：%s"%(time.perf_counter()-soup_timer))
	with open(HTML_DIR+"//"+con_type+" "+start+"-"+end+".html","w",encoding="utf-8") as f:
		f.write(soup.prettify())
	print("输出HTML耗时%s"%(time.perf_counter()-timer))
	print("输出结束 %s-%s\n"%(start,end))

def build_HTML(cont_info_dict,con_type):
	a=0
	day_start=""#存储其实日期
	day_end=""#最后结束时的日期
	msgBoxes_list=[]
	timer=0.0
	for CID in cont_info_dict.keys():
		if a==0:#分页的起始
			timer=time.perf_counter()#设置定时器
			html,day=build_msgBox(CID)
			day_start=day#起始日期
			print("起始日期："+day_start)
			day_end=day
			msgBoxes_list.append(html)
		else:#如果不是起始页
			html,day=build_msgBox(CID)
			day_end=day
			msgBoxes_list.append(html)
		a+=1
		if a==CUT:#加完之后等于分割数，则分页结
			a=0#重置计数器
			print("遍历用时：%s"%(time.perf_counter()-timer))
			export_html(day_start,day_end,msgBoxes_list,con_type)
			msgBoxes_list.clear()
	#处理不足一整页的余下的信息
	if len(msgBoxes_list)!=0:
		export_html(day_start,day_end,msgBoxes_list,con_type)

def build_dir(dir):
	if not os.path.isdir(dir):
		os.mkdir(dir)

#uname = input("请输入用户ID：@")
uname="wanglei19990921"
print ("你输入的用户ID是: " + uname)
c=openSQLite(uname)



HTML_DIR="HTML"#输出文件存储目录

select_type=input("请输入选择的表：0,MINE 广播; 1,FAVOR 收藏; 2,AT 提及\n")
TYPE_DICT={
	0:{"IMG_DIR":"images/mine_images","IMG_TABLE":"IMAGE","CON_TABLE":"MINE"},
	1:{"IMG_DIR":"images/favor_images","IMG_TABLE":"FIMAGE","CON_TABLE":"FAVOR"},
	2:{"IMG_DIR":"images/mine_images","IMG_TABLE":"IMAGE","CON_TABLE":"AT"}
	}

IMG_DIR=TYPE_DICT[int(select_type)]["IMG_DIR"]
IMG_TABLE=TYPE_DICT[int(select_type)]["IMG_TABLE"]
CON_TABLE=TYPE_DICT[int(select_type)]["CON_TABLE"]#输出的HTML前会带有表名


build_dir(HTML_DIR)
build_ext_dict(IMG_DIR,img_file_dict)
build_img_dict(c,IMG_TABLE,img_info_dict)
build_content_list(c,CON_TABLE,cont_info_dict)
build_video_dict(c)
build_HTML(cont_info_dict,CON_TABLE)