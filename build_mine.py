import os
import sqlite3
import re
img_file_dict={}
img_info_dict={}
cont_info_dict={}

def build_ext_dict(dir,dict):#输入空字典，构建文件名扩展名对照 dict[文件名,.扩展名]
	for file in os.listdir(os.getcwd()+"\\"+dir):
		name=os.path.splitext(file)[0]
		ext=os.path.splitext(file)[1]
		dict[name]=ext
		
def getTag_Image(dir,img_file_dict,CID):#根据CID构建
	#传入CID，数据库查IMAGE找对应图片，如果存在返回img标签，不存在则返回空字符串
	img_tag=""
	if CID in img_info_dict.keys():
		dict=img_info_dict[CID]
		for img in sorted(dict.keys()):#img是一个int类型的index
			url=dict[img]
			name=url[url.rfind("/")+1:]#处理链接
			if name in img_file_dict.keys():
				name="../"+dir+"/"+name+img_file_dict[name]#得到完整文件名
				img_tag=img_tag+'<div class="imgItem"> <img class="image" src="'+name+'"> </div>\n'
			img_tag='<div class="picBox">\n'+img_tag+'</div>\n'
	else:
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

def build_img_dict(c,img_table,img_info_dict):
	sql_list=c.execute("SELECT * FROM "+img_table)
	for img in sql_list:
		if img[0] not in img_info_dict.keys():#如果不存在这个
			img_info_dict[img[0]]={}
		img_info_dict[img[0]][img[1]]=img[2]

def build_content_list(c,content_table,cont_info_dict):
	sql_list=c.execute("SELECT * FROM "+content_table+" ORDER BY TID")
	for content in sql_list:
		cont_info_dict[content[0]]={"TID":content[1],"TYPE":content[2],"AUTHOR":content[3],"CONTENT":content[4],"TIME":content[5],"QAUTHOR":content[6],"QCONTENT":content[7],"QTIME":content[8],"MOOD":content[9],"LOCATION":content[10],"LONGITUDE":content[11],"LATITUDE":content[12]}

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
build_ext_dict("mine_images",img_file_dict)
build_img_dict(c,"IMAGE",img_info_dict)
build_content_list(c,"MINE",cont_info_dict)