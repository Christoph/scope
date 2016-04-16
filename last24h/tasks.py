from __future__ import absolute_import

from celery import shared_task, current_task

from time import sleep

import sys
from django.templatetags.static import static

import Queue
import threading
import time
import networkx as nx
import feedparser
import newspaper
from newspaper import Article
import untangle
import sys
import json
import urllib
import math
from time import mktime
from datetime import timedelta
from datetime import datetime
import copy
from last24h.models import Suggest, Query
from django.conf import settings
#import logging

global workQueue, exitFlag, queueLock, current_name, articlenumber

class myThread (threading.Thread):
	def __init__(self, threadID, name, q):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.q = q
		#self.counter = counter
	def run(self):
		print "Starting " + self.name
		process_data(self.name, self.q)
		
		print "Exiting " + self.name



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


exitFlag = 0



@shared_task
def add(x, y):
	for i in range(100):
		sleep(0.1)
	return x+y
		


@shared_task
def mul(x, y):
	return x * y


@shared_task
def xsum(numbers):
	return sum(numbers)


@shared_task
def do_work():
	for i in range(100):
		sleep(0.1)
		print i
		current_task.update_state(state='PROGRESS',
			meta={'current': i, 'total': 100})


@shared_task
def cs_task(feeds,strin,alert):
	from celery import shared_task, current_task
	import gensim
	import nltk
	import re
	import string
	import numpy
	import scipy
	#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
	sys.argv = [settings.STATIC_BREV + static('last24h/cs2.py'), feeds, strin, current_task,alert]
				#return returncode
	if alert == 0:
		current_task.update_state(state='PREPARE',
			meta={'current': 10, 'articles':0, 'words':0})
	execfile(settings.STATIC_BREV + static('last24h/cs2.py'))#'/home/django/graphite/static/last24h/cs2.py')         

