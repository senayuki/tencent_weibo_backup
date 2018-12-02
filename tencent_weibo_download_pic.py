import imghdr  
import urllib
from urllib import request
import os
import util
import sqlite3
def get_name(url):
	n=-1
	t=""
	i=0
	aflag=True
	imageflag = False#默认False是带有扩展名的，Ture是URL无扩展名，+'/2000'
	while(t!="/"):
		t=url[n]
		n=n-1
		i+=1
	if i<6:
		aflag=False
		url = url[:n+1]
		url,urlid = get_name(url)
	else:
		urlid = url[n+2:]
	n=-1
	t=""
	try:#如果出现错误说明没有找到点号，urlid已经是文件名
		while(t!="."):
			t=urlid[n]
			if urlid[n] == ".":
				break
			n=n-1
		urlid = urlid[:n]
	except:
		imageflag = True
		if aflag and (url[10:17] == 'qpic.cn'):
			url = url +'/2000'
		else:
			None
	return url,urlid
	
def download_core(type,url,urlid):
	flag = False
	for fn in list:
		if urlid == fn:
			flag = True
			break
	print('图片名称：'+urlid)
	if flag:
		print('图片已经存在')
		print('----------------------------------------------------------------------------------')
	else:
		try:
			print('下载中……')
			flag_404 = True
			response = urllib.request.urlopen(url,timeout=10)
			imagefile = response.read()
		except:
			flag_404 = False
		if flag_404:
			try:
				extension = imghdr.what('', imagefile)
				filename = '.\\'+type+'_images\\' + urlid + '.'+extension
			except:
				print('无法判断格式，已经默认设置为jpeg格式')
				util.add_log('无法判断格式，已经默认设置为jpeg格式：'+url)
				extension = 'jpeg'
				filename = '.\\'+type+'_images\\' + urlid + '.'+extension
			print('下载成功：'+urlid + '.'+extension)
			with open(filename, 'wb') as f:
				try:
					f.write(imagefile)
					f.close()
					print('----------------------------------------------------------------------------------')
				except:
					print('图片保存失败！')
					print('----------------------------------------------------------------------------------')
		else:
			print('出现错误，图片可能已经404')
			print('----------------------------------------------------------------------------------')
			util.add_log('出现错误，图片可能已经404：'+url)
	
def get_url(image_list):
	index = 1
	for row in image_list:
		print('第 %s 条。' % index)
		index+=1
		url = (row[0])
		url,urlid = get_name(url)
		print('图片地址：'+url)
		download_core(type,url,urlid)
	list = []
	util.add_log('下载了 %s 条' % index)


util.add_log('图片下载启动')
cwd = os.getcwd()
#uname = input("请输入用户ID：@")
uname = 'wanglei19990921'
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

print('----------------------------------------------------------------------------------')
type='emoji'
if not os.path.exists('.//images//'+type+'_images'):
	os.mkdir('.//images//'+type+'_images')
	util.add_log('新建'+type+'_images目录成功')
print('开始下载EMOJI图片')
olist = os.listdir(r'./'+type+r'_images')
list = []
for files in olist:
	list.append(os.path.splitext(files)[0])
util.add_log('开始下载EMOJI图片')
print('----------------------------------------------------------------------------------')
image_list = c.execute("SELECT DISTINCT URL FROM EMOJI")
get_url(image_list)
print('EMOJI图片下载完毕')
print('----------------------------------------------------------------------------------')
util.add_log('EMOJI图片下载完毕')

print('----------------------------------------------------------------------------------')
type='video'
if not os.path.exists('.//images//'+type+'_images'):
	os.mkdir('.//images//'+type+'_images')
	util.add_log('新建'+type+'_images目录成功')
print('开始下载视频图片')
olist = os.listdir(r'./'+type+r'_images')
list = []
for files in olist:
	list.append(os.path.splitext(files)[0])
util.add_log('开始下载视频图片')
print('----------------------------------------------------------------------------------')
image_list = c.execute("SELECT DISTINCT COVER FROM VIDEO")
get_url(image_list)
print('视频图片下载完毕')
print('----------------------------------------------------------------------------------')
util.add_log('视频图片下载完毕')

print('----------------------------------------------------------------------------------')
type='mine'
if not os.path.exists('.//images//'+type+'_images'):
	os.mkdir('.//images//'+type+'_images')
	util.add_log('新建'+type+'_images目录成功')
print('开始下载原文图片')
olist = os.listdir(r'./'+type+r'_images')
list = []
for files in olist:
	list.append(os.path.splitext(files)[0])
util.add_log('开始下载原文图片')
print('----------------------------------------------------------------------------------')
image_list = c.execute("SELECT DISTINCT URL FROM IMAGE")
get_url(image_list)
print('原文图片下载完毕')
print('----------------------------------------------------------------------------------')
util.add_log('原文图片下载完毕')

print('----------------------------------------------------------------------------------')
type='favor'
if not os.path.exists('.//images//'+type+'_images'):
	os.mkdir('.//images//'+type+'_images')
	util.add_log('新建'+type+'_images目录成功')
print('开始下载收藏图片')
olist = os.listdir(r'./'+type+r'_images')
list = []
for files in olist:
	list.append(os.path.splitext(files)[0])
util.add_log('开始下载收藏图片')
print('----------------------------------------------------------------------------------')
image_list = c.execute("SELECT DISTINCT URL FROM FIMAGE")
get_url(image_list)
print('收藏图片下载完毕')
print('----------------------------------------------------------------------------------')
util.add_log('收藏图片下载完毕')

print('----------------------------------------------------------------------------------')
type='PM'
if not os.path.exists('.//images//'+type+'_images'):
	os.mkdir('.//images//'+type+'_images')
	util.add_log('新建'+type+'_images目录成功')
print('开始下载收藏图片')
olist = os.listdir(r'./'+type+r'_images')
list = []
for files in olist:
	list.append(os.path.splitext(files)[0])
util.add_log('开始下载私信图片')
print('----------------------------------------------------------------------------------')
image_list = c.execute("SELECT DISTINCT URL FROM PMIMAGE")
get_url(image_list)
print('私信图片下载完毕')
print('----------------------------------------------------------------------------------')
util.add_log('私信图片下载完毕')
