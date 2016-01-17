#import schedule
import time
import urllib
import threading
import Queue
import os
import datetime
import sys
from django.core.mail import send_mail
from last24h.models import Suggest, Alert, Send
from django_cron import CronJobBase, Schedule


global workQueue, exitFlag, queueLock, to_send

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
            #print " %s processing" % (threadName)
        else:
            queueLock.release()
            #print " %s release" % (threadName)
        time.sleep(1)
        
queueLock = threading.Lock()
exitFlag = 0


class UpdateIndex(CronJobBase):
    RUN_AT_TIMES = ['6:30', '12:30', '18:30','23:08','22:08','00:08']

    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'graphite.update_index'    # a unique code

    def do(self):
        execfile('/home/django/graphite/static/last24h/clean4.py')    # do your thing here
    
class SendAlerts(CronJobBase):
    RUN_EVERY_MINS = 60

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'graphite.send_alerts'    # a unique code

    def do(self):
        alerts()   # do your thing here



def clean_queries():
    filelist = [ f for f in os.listdir("/home/django/graphite/static/last24h/q") if f != '.ipynb_checkpoints']
    for f in filelist:
        os.remove(f)
    filelist = [ f for f in os.listdir("/home/django/graphite/static/last24h/cs") if f != '.ipynb_checkpoints']
    for f in filelist:
        os.remove(f)
    suggestions = Suggest.objects.all().exclude(custom = 'last24h')
    suggestions.delete()
    print "cleaned database"
    #suggestions = Suggest.objects.filter(custom__startswith = 'us')
    #suggestions.delete()
        
    
def update_l24h():
    #execfile('last24h/cleaned_up.py') 
    execfile('/home/django/graphite/static/last24h/clean4.py') 


def alerts():
    time_at_beginning = datetime.datetime.now().replace(second = 0, microsecond = 0, minute = 0)
    for job in Send.objects.all():
        entry = [job.email,job.query,job.user,job.string]
        if entry[2] != None:
            address = entry[2].first_name + ' ' + entry[2].last_name
        else: 
            address = 'there'
        send_mail('Your latest Grews alert for: ' + entry[1], 'Hi' + address + ',here is the link to your latest grews alert for your query:' + entry[1] + 'http://127.0.0.1:8000/last24h/cs=' + entry[3] + 'If you have a profile with us, you can edit the alert at any time from your profile. Otherwise click this link to delete the alert: http://127.0.0.1:8000/last24h/d=' + entry[3], 'valentinjohanncaspar@gmail.com', [entry[0]], connection=None, html_message='<head><title>grews | maximise relevance, minimise redundancy</title></head><p>Hi '+ address + ',</p><p>here is the link to your latest grews alert for your query:</p><p><a href="http://127.0.0.1:8000/last24h/cs=' + entry[3] + '" >' + entry[1] + '</a></p><p>If you have a profile with us, you can edit the alert at any time from your profile. Otherwise you can delete your alert by clicking <a href="http://127.0.0.1:8000/last24h/d=' + entry[3]+'">here</a>.</p>')    
    Send.objects.all().delete()
    for alert in Alert.objects.all():
        #send mails to all in to_send
        delivery_t = datetime.datetime.now().replace(second = 0, microsecond = 0, minute = 0) + datetime.timedelta(hours = 1)
        diff_in_sec = delivery_t - alert.delivery_time.replace(tzinfo = None, minute= 0)                                                                                    
        if (int(diff_in_sec.total_seconds()) % alert.frequency == 0) and (diff_in_sec.total_seconds() > 0) :
            topics = alert.query.split(',')
            for i in range(0, len(topics)):
                topics[i] = topics[i].strip(' ') 
            string = topics.replace(',','AND') + '_' + delivery_t.isoformat()[:13] 
            sys.argv = ['last24h/static/last24h/cs.py',topics,string,alert]
            execfile('last24h/static/last24h/cs.py')
            q = Send(email = alert.email, query = alert.query, user = alert.user,string = string)
            q.save()
                                                                                             
                                                                                          
#schedule.every(4).hours.do(update_index_graph)
#schedule.every(3).hours.do(clean_queries)
#schedule.every().hour.at("00:00").do(alerts)

#while True:
 #   schedule.run_pending()
#  time.sleep(1)