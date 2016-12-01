from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
import time
import urllib
import threading
import Queue
import os
import datetime
import sys
from django.core.mail import send_mail
# from last24h.models import Alert, Send, Sources, Query, Suggest
# from django_cron import CronJobBase, Schedule
import networkx as nx
import gensim
import nltk
import re
import string
import numpy
import scipy
import feedparser
import newspaper
from newspaper import Article
import untangle
# import sys
import json
from django.conf import settings
from django.templatetags.static import static

from conf.tasks import brief_rene

global workQueue, exitFlag, queueLock,finalurl

class myThread (threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
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
            #data.nlp()
            print " %s processing" % (threadName)
        else:
            queueLock.release()
            print " %s release" % (threadName)
        time.sleep(1)



class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('n1', nargs='+', type=int)
        parser.add_argument('n2', nargs='+', type=int)


    def handle(self,*args,**options):
        delivery_t = datetime.datetime.now().replace(second = 0, microsecond = 0, minute = 0) + datetime.timedelta(hours = 1)
        strin = delivery_t.isoformat()[:13] + "&feeds=none&term=rene_likes_tech"
        print options['n1']
        print options['n2']
        n1 = options['n1'][0]
        n2 = options['n2'][0]

        # sys.argv = [settings.STATIC_BREV + static('last24h/rene.py'), strin,n1,n2]
        # execfile(settings.STATIC_ROOT + 'last24h/rene.py')
        sys.argv = ['curate/customers/create_newsletter_nh.py', strin, n1, n2]
        execfile('curate/customers/create_newsletter_nh.py')
        address = "Rene"

        strin = strin

 #        entry = ['grphtcontact@gmail.com',"Rene's Newsletter", "Rene",strin]
 #        send_mail('Your latest alert for: ' + entry[1], 'Hi' + address + ', here is the link to your latest alert for your query:' + entry[1] +
 # settings.CURRENT_DOMAIN + '/last24h/cs=' + entry[3] + 'You can manage your alerts in your profile settings. Hope you enjoy the graph!', 'grphtcontact@gmail.com', [entry[0]],
 # connection=None, html_message='<head><title>'+ settings.CURRENT_NAME + '| maximise relevance, minimise redundancy</title></head><p>Hi '+
 # address + ',</p><p>here is the link to your latest alert for your query:</p><p><a href="'
 # + settings.CURRENT_DOMAIN + '/last24h/cs=' + entry[3] + '" >' + entry[1] +
 # '</a></p><p>You can manage your alerts in your profile settings. Hope you enjoy the graph!</p>')
 #        brief_rene('grphtcontact@gmail.com',strin,0)

 #        n2 = 18
 #        strin = strin + str(n2)

 #        sys.argv = [settings.STATIC_BREV + static('last24h/rene.py'), strin,n1,n2]
 #        execfile(settings.STATIC_ROOT + 'last24h/rene.py')

 #        entry = ['grphtcontact@gmail.com',"Rene's Newsletter", "Rene",strin]
 #        send_mail('Your latest alert for: ' + entry[1], 'Hi' + address + ', here is the link to your latest alert for your query:' + entry[1] +
 # settings.CURRENT_DOMAIN + '/last24h/cs=' + entry[3] + 'You can manage your alerts in your profile settings. Hope you enjoy the graph!', 'grphtcontact@gmail.com', [entry[0]],
 # connection=None, html_message='<head><title>'+ settings.CURRENT_NAME + '| maximise relevance, minimise redundancy</title></head><p>Hi '+
 # address + ',</p><p>here is the link to your latest alert for your query:</p><p><a href="'
 # + settings.CURRENT_DOMAIN + '/last24h/cs=' + entry[3] + '" >' + entry[1] +
 # '</a></p><p>You can manage your alerts in your profile settings. Hope you enjoy the graph!</p>')
 #        brief_rene('grphtcontact@gmail.com',strin)

 #        entry = ['grphtcontact@gmail.com',"Rene's Newsletter", "Rene",strin]
 #        send_mail('Your latest alert for: ' + entry[1], 'Hi' + address + ', here is the link to your latest alert for your query:' + entry[1] +
 # settings.CURRENT_DOMAIN + '/last24h/cs=' + entry[3] + 'You can manage your alerts in your profile settings. Hope you enjoy the graph!', 'grphtcontact@gmail.com', [entry[0]],
 # connection=None, html_message='<head><title>'+ settings.CURRENT_NAME + '| maximise relevance, minimise redundancy</title></head><p>Hi '+
 # address + ',</p><p>here is the link to your latest alert for your query:</p><p><a href="'
 # + settings.CURRENT_DOMAIN + '/last24h/cs=' + entry[3] + '" >' + entry[1] +
 # '</a></p><p>You can manage your alerts in your profile settings. Hope you enjoy the graph!</p>')
 #        brief_rene('grphtcontact@gmail.com',strin)
