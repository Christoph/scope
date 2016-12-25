global exitFlag, workQueue, queueLock, articlenumber


# from django.core.management.base import BaseCommand
import networkx as nx
import gensim
import nltk
import re
import string
import feedparser
import newspaper
from newspaper import Article
import Queue
import threading
import time
import untangle
import sys
import json
import urllib
import math
# from django.core.mail import send_mail
from time import mktime
from datetime import datetime
# from last24h.models import Suggest
# from django.conf import 'last24h/static/rt numpy
import scipy
import email, imaplib, os,sys
import urllib2
import datetime
from datetime import date,timedelta, datetime
from urlparse import urlparse
from eventregistry import *

# def download_er(query):

er = EventRegistry()
q = QueryArticles(lang = 'deu')
# set the date limit of interest
#q.setDateLimit(datetime.date(2014, 4, 16), datetime.date.today())
# find articles mentioning the company Apple
q.addConcept(er.getConceptUri(query))
# return the list of top 30 articles, including the concepts, categories and article image
q.addRequestedResult(RequestArticlesInfo(count = 200, sortBy = "fb",
    returnInfo = ReturnInfo(articleInfo = ArticleInfoFlags(concepts = True, categories = True, image = True))))
res = er.execQuery(q)

print str(res)[0:100]
results = res['articles']['results']

# with open('last24h/static/commerz/er_' + query + .txt',"w+") as h:
#     json.dump(results,h)

query_string = "_".join(query.split(" "))
# articles_info= []
# for i in results:
#     tup = tuple([int(j) for j in tuple(i['date'].split('-') + i['time'].split(':'))+(0,1,-1)])
#     ha = datetime.datetime.fromtimestamp(mktime(tup))
#     articles_info.append([i['url'],ha])


reload(sys)
sys.setdefaultencoding('utf8')

articles = [Article(results[i]['url'],language="de") for i in range(0,len(results))]

# for article in articles_info:

# 	articles.append(Article(article[0],language="de"))




upper = min(600, len(articles))

# for a in articles:
#     a.download()
#     a.parse()
    
# print "Start threading"

# #Threading stuff

exitFlag = 0

exitFlag = 0
counter = 1
class myThread (threading.Thread):
	def __init__(self, threadID, name, q):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.q = q
	def run(self):
		print "Starting " + self.name
		process_data(self.name, self.q)
		# current_task.update_state(state='DOWNLOAD',
		# meta={'current': 10 + int(counter/articlenumber)*50, 'articles':articlenumber, 'words':0})
		# counter += 1
		# print "Exiting " + self.name

def process_data(threadName, q):
	while not exitFlag:
		queueLock.acquire()
		if not workQueue.empty():
			data = q.get()
			queueLock.release()
			data.download()
			data.parse()
			print " %s processing" % (threadName)
		else:
			queueLock.release()
			print " %s release" % (threadName)
		time.sleep(1)

maxthread = 200
if upper < maxthread:
   threadlimit = upper
else:
   threadlimit = maxthread
        
threadList = []
for i in range(1,threadlimit):
   threadList.append(str(i))

nameList = articles
queueLock = threading.Lock()
workQueue = Queue.Queue(upper)
threads = []
threadID = 1

#Create new threads
for tName in threadList:
   thread = myThread(threadID, tName, workQueue)
   thread.start()
   threads.append(thread)
   threadID += 1

#Fill the queue
queueLock.acquire()
for word in nameList:
   workQueue.put(word)
queueLock.release()


#Wait for queue to empty
while not workQueue.empty():
  pass

#Notify threads it's time to exit
exitFlag = 1

#Wait for all threads to complete
for t in threads:
   t.join()
print "Exiting Main Thread"

#Putting together



# doc = [ ]
# keywords = []
# summary = []
# titles = []
# urls = []
# times = []
# images = []
# exclude = set(('', 'FT.com / Registration / Sign-up','Error','404 Page not found','Page no longer available', 'File or directory not found','Page not found','Content not found','Seite nicht gefunden','404 :: lr-online'))
# sources = []
# unsubscribe_exclude = "If you are not redirected automatically, please click the Unsubscribe button below"

# counter = 0
# words_total = 0
for i in range(0,upper):
    article = articles[i]
    # words_total += len(" ".join(article.text))
    results[i]['body'] = article.text
    results[i]['image'] = article.top_image
    # if article.title not in exclude and unsubscribe_exclude not in article.text:# and "tech" in article.text:
    #     doc.append(article.text)
    #     titles.append(article.title)
    #     urls.append(article.url)
    #     images.append(article.top_image)
    #     times.append(articles_info[i][1])
    #     summary.append(article.text[0:400] + "...")
    #     sources.append()

with open('last24h/static/commerz/er_' + query_string + '_ger.json',"w+") as h:
    json.dump(results,h)
