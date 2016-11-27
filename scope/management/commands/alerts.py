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
from last24h.models import Alert, Send,Sources, Query
#from django_cron import CronJobBase, Schedule                     
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
#import sys
import json
from django.conf import settings

#from last24h.tasks import alert_task

global workQueue, exitFlag, queueLock

from last24h.tasks import cs_task

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
            data.nlp()
            print " %s processing" % (threadName)
        else:
            queueLock.release()
            print " %s release" % (threadName)
        time.sleep(1)



class Command(BaseCommand):

    def handle(self,*args,**options):
        time_at_beginning = datetime.datetime.now().replace(second = 0, microsecond = 0, minute = 0)
        for job in Send.objects.all():
            entry = [job.user.email,job.query,job.user,job.string]
            if entry[2] != None:
                address = entry[2].first_name + ' ' + entry[2].last_name
            else:
                address = 'there'
            send_mail('Your latest alert for: ' + entry[1], 'Hi' + address + ', here is the link to your latest alert for your query:' + entry[1] +
 settings.CURRENT_DOMAIN + '/last24h/cs=' + entry[3] + 'You can manage your alerts in your profile settings. Hope you enjoy the graph!', 'grphtcontact@gmail.com', [entry[0]],
 connection=None, html_message='<head><title>'+ settings.CURRENT_NAME + '| maximise relevance, minimise redundancy</title></head><p>Hi '+
 address + ',</p><p>here is the link to your latest alert for your query:</p><p><a href="'
 + settings.CURRENT_DOMAIN + '/last24h/cs=' + entry[3] + '" >' + entry[1] +
 '</a></p><p>You can manage your alerts in your profile settings. Hope you enjoy the graph!</p>')
        Send.objects.all().delete()
        delivery_t = datetime.datetime.now().replace(second = 0, microsecond = 0, minute = 0) + datetime.timedelta(hours = 1)
        for alert in Alert.objects.all():
            #send mails to all in to_send
            diff_in_sec = delivery_t - alert.delivery_time.replace(tzinfo = None, minute= 0)
            #print int(diff_in_sec.total_seconds()) % alert.frequency
            if (int(diff_in_sec.total_seconds()) % alert.frequency == 0) and (diff_in_sec.total_seconds() > 0) :
                feeds = alert.feeds.split(',')
                if alert.feed_type == False:
                    topics = alert.query.split(',')
                    strin = delivery_t.isoformat()[:13] + "&feeds=none&term=" + "AND".join(topics)
                else: 
                    ids = []
                    for feed in feeds:
                        source = Sources.objects.get(url=feed)
                        ids.append(str(source.id))
                    strin = delivery_t.isoformat()[:13] + "&feeds=" + "AND".join(ids) + "&term=none"

                cs_task(feeds,strin,1)
                q = Query(user = alert.user, query = alert.query, time = delivery_t, string = strin, url = reverse('csr',args=[strin]))
                q.save()
                q = Send(query = alert.query, user = alert.user,string = strin)
                q.save()

