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
import nltk.classify.util
from nltk.classify import NaiveBayesClassifier
from nltk.corpus import movie_reviews


reload(sys)
sys.setdefaultencoding('utf8')


query = "Volkswagen"
query2 = "Volkswagen_Group"

results = json.loads(open('last24h/static/commerz/er_' + query + '_ger.json').read())

results2 = json.loads(open('last24h/static/commerz/er_' + query2 + '_ger.json').read())


exclude = set(('', 'FT.com / Registration / Sign-up','Error','404 Page not found','Page no longer available', 'File or directory not found','Page not found','Content not found','Seite nicht gefunden','404 :: lr-online','kinja.com'))

unsubscribe_exclude = "If you are not redirected automatically, please click the Unsubscribe button below"




doc = [a['body'] for a in results if (a['title'] not in exclude and unsubscribe_exclude not in a['body'] and a['isDuplicate'] == False)]

for i in range(0,len(results2)):
	a = results2[i]
	if (a['title'] not in exclude and unsubscribe_exclude not in a['body'] and a['isDuplicate'] == False):
		doc.append(a['body'])




