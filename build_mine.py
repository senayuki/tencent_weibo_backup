import os
import util
import sqlite3
import re
img_mine_dict={}
#处理content中的emoji

SQL="SELECT * FROM MINE LEFT JOIN IMAGE ON MINE.CID=IMAGE.CID GROUP BY MINE.CID ORDER BY MINE.TID,IMAGE.RANK"
def build_ext_dict(dir,dict):#输入空字典，构建文件名扩展名对照 dict[文件名,.扩展名]
	for file in os.listdir(os.getcwd()+"\\"+dir):
		name=os.path.splitext(file)[0]
		ext=os.path.splitext(file)[1]
		dict[name]=ext
		
def getTag_Image(table,dir,dict,CID):#根据CID构建
	#传入CID，数据库查IMAGE找对应图片，如果存在返回img标签，不存在则返回空字符串
		img_tag=""
		img_sql=c.execute("SELECT URL FROM "+table+" WHERE CID='"+str(CID)+"'")#查找这条私信是否附有图片
		try:#遍历查询结果，如果为空，报异常退出
			for img in img_sql:
				url=img[0]
				name=url[url.rfind("/")+1:]#处理链接
				if name in imglist.keys():
					name="../"+dir+"/"+name+dict[name]#得到完整文件名
					img_tag=img_tag+'<div class="imgItem"> <img class="image" src="'+name+'"> </div>\n'
			img_tag='<div class="picBox">\n'+img_tag+'</div>'
		except:
			None
		return img_tag
def emojiInContent(content):#处理正文的emoji
	pattern_emoji = re.compile(r'(<emoji=.*?>)', re.S)
	emoji_urls=re.findall(pattern_emoji, content)
	for emoji in emoji_urls:
		file_name=emoji[emoji.rfind("/")+1:-2]
		content=content.replace(emoji,'<img class"emoji" src="../emoji_images/'+file_name+'">')
	return content

def imgInContent(dir,dict,content):#处理正文中的图片链接
	pattern_img = re.compile(r'(<img=.*?>)', re.S)
	img_urls=re.findall(pattern_img, content)
	for img in img_urls:
		file_name=img[img.rfind("/")+1:-2]
		file_name=file_name+dict[file_name]#需要添加查找图片判断扩展名并添加，因为img本来就不带扩展名
		content=content.replace(img,'<a class"imgInContent" href="../'+dir+'/'+file_name+'" target="_Blank"><i>图片</i></a>')
	return content

def build_content_list(content_table,img_table):
	SQL="SELECT * FROM MINE LEFT JOIN IMAGE ON MINE.CID=IMAGE.CID GROUP BY MINE.CID ORDER BY MINE.TID,IMAGE.RANK"
def openSQLite(uname):
	if (os.path.exists(uname+'.db')):
		conn = sqlite3.connect(uname+'.db')
		c = conn.cursor()
		print('打开数据库成功')
	else:
		print('未能找到数据库')
		exit()
	return c

#uname = input("请输入用户ID：@")
uname="wanglei19990921"
print ("你输入的用户ID是: " + uname)
c=openSQLite(uname)
build_ext_dict("mine_images",img_mine_dict)
print(imgInContent("MINE_images",img_mine_dict,content))