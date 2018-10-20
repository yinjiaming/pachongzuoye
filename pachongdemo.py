import multiprocessing as mp
from pymysql.connections import Connection
from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
from concurrent.futures import ProcessPoolExecutor
import pymysql
def crawl(url):
	response=urlopen(url)
	return response.read().decode()
def parse(html):
	soup=BeautifulSoup(html,'html.parser')
	all_href=soup.find_all('a',{"href":re.compile('^/2018/.+?/.+?/page.htm')})
	all_href = ["http://news.xmu.edu.cn"+l['href'] for l in all_href]
	return all_href

def job1(pages):
	db=Connection(host="localhost",user="root",password="283732",port=3306,database='world',charset='gbk')
	cur=db.cursor()
	for i in range(pages[0],pages[1]):
		url1="http://news.xmu.edu.cn/1552/list"+str(i)+".htm"
		html=crawl(url1)
		urls=parse(html)

		for url in urls:
			html=urlopen(url).read().decode('utf-8')
			soup=BeautifulSoup(html,'html.parser')
			title=soup.find('span', {"class":'Article_Title'})
			title=title.get_text()
			readnum=soup.find('span',{"class":'WP_VisitCount'},{"style":'display'})
			readnum=readnum.get_text()
			date=soup.find('span',{"class":'Article_PublishDate'})
			date=date.get_text()
			print("url="+url)
			insert_xmunews = 'insert into xmunews3(title,date1,url,views) values(%s,%s,%s,%s);'
			try:
				cur.execute(insert_xmunews,[title,date,url,readnum])
			except Exception as e:
				print("！！！！！！！！！！异常是%s" % e)
			print("题目："+title)
			print("浏览次数："+readnum)
			print("发布日期："+date)
			db.commit()
	cur.close()
	db.close()
if __name__ == '__main__':
	#sql="""create table xmunews(title char(30),date char(10),url char(50),views char(4))"""
	#cur.execute(sql)
	#cur.execute("select * from xmunews")
	#row = cur.fetchall()
	# pool=mp.Pool(4)
	# pool.map(job1,(range(53)))
	pages = [(1,15),(15,30),(30,40),(40,53)]
	with ProcessPoolExecutor() as excute:
		excute.map(job1,pages)
