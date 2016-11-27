from __future__ import absolute_import

from celery import shared_task, current_task
from celery.exceptions import Reject
from time import sleep, mktime

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
import re
import math
import gensim
import nltk
import string
from datetime import timedelta
from datetime import datetime
import copy
from last24h.models import Suggest, Query
from django.conf import settings
#import logging
from networkx.readwrite import json_graph
from django.core.mail import send_mail

global workQueue, exitFlag, queueLock, current_name, articlenumber, inputt

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
def test_task(email):
	print email 

@shared_task
def twitter_job(twitt_input):
	#from celery import shared_task, current_task
	#import json
	inputdict = {"inputt": twitt_input}
	print inputdict
	#sys.argv = [settings.STATIC_BREV + static('last24h/tweet.py'), inputt]
	execfile(settings.STATIC_ROOT + 'last24h/tweet.py',inputdict)

@shared_task
def brief_rene(email,strin,select):
	#import networkx as nx
	#import gensim
	#import nltk
	#import re
	#import string
	#import json
	#import urllib
	#from networkx.readwrite import json_graph
	#from django.core.mail import send_mail
	#from last24h.models import Suggest
	#from django.conf import settings
#	try:
	#sys.argv = [email]
	sys.argv = [settings.STATIC_BREV + static('last24h/create_brief_rene.py'), strin, email,select]
	execfile(settings.STATIC_ROOT + 'last24h/create_brief_rene.py')


@shared_task
def sample_brief(email):
	#import networkx as nx
	#import gensim
	#import nltk
	#import re
	#import string
	#import json
	#import urllib
	#from networkx.readwrite import json_graph
	#from django.core.mail import send_mail
	#from last24h.models import Suggest
	#from django.conf import settings
	#try:
	#sys.argv = [email]
	execfile(settings.STATIC_ROOT + 'last24h/create_brief.py')
	#except:
	#	raise Exception()

@shared_task
def cs_task(feeds,strin,alert):
	#from celery import shared_task, current_task
	#import gensim
	#import nltk
	#import re
	#import string
	import numpy
	import scipy
	#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
	sys.argv = [settings.STATIC_BREV + static('last24h/customsearch.py'), feeds, strin, current_task,alert]
				#return returncode
	if alert == 0:
		current_task.update_state(state='PREPARE',
			meta={'current': 10, 'articles':0, 'words':0})
	
	execfile(settings.STATIC_ROOT + 'last24h/customsearch.py')#settings.STATIC_BREV + static('last24h/cs2.py'))
	#except:
	#	raise Exception()
			
	def on_failure(self, *args, **kwargs):
	 	pass
