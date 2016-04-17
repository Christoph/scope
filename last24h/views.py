from django.shortcuts import render, get_object_or_404, render_to_response
from django.template import RequestContext, loader
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, AnonymousUser
from django.templatetags.static import static
from django.conf import settings
from django.db import connections
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render

from .forms import NameForm, AlertForm
from .models import Suggest, Alert, Query
import sys

import threading
import Queue
import time
import datetime

global workQueue, exitFlag, queueLock, current_name

current_name = settings.CURRENT_NAME

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

exitFlag = 0

def check_login(request):
    if request.user.is_authenticated():
        log_inf = ['Profile','Logout']
        log_link = ['profile','logout_user']
    else: 
        log_inf = ['Register','Login']
        log_link = ['register','login_user']
    return log_inf, log_link

#@login_required(login_url='/login')
def index(request):

    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        form2 = NameForm(request.POST)
        # check whether it's valid:
        print request.POST
        if (form.is_valid()) and ('filter' in request.POST):
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            topic = form.cleaned_data['query_text']
            topics = topic.split(',')
            for i in range(0, len(topics)):
                topics[i] = topics[i].strip(' ').lower().replace(" ","_").replace("_"," ")
            strin = "AND".join(topics) + '_' + datetime.datetime.now().isoformat()[:13]
            print topics
            sys.argv = ['/home/django/graphite/static/last24h/csl24h.py', topics, strin]
            execfile('/home/django/graphite/static/last24h/csl24h.py')
            #return returncode
            
        
            return HttpResponseRedirect(reverse('last24h:csresults',args=[strin])) 
        if (form2.is_valid()) and ('customsearch' in request.POST):
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            topic2 = form2.cleaned_data['query_text']
            topics = topic2.split(',')
            for i in range(0, len(topics)):
                topics[i] = topics[i].strip(' ').lower().replace(" ","_").replace("_"," ")
            strin = "AND".join(topics) + '_' + datetime.datetime.now().isoformat()[:13]
            print topics
            if request.user.is_authenticated():
                q = Query(user = User.objects.get(id =request.user.id), query = topic2, time = datetime.datetime.now(), string = strin, url = reverse('csr',args=[strin]))
                q.save()
            sys.argv = ['/home/django/graphite/static/last24h/cs2.py', topics, strin]
            execfile('/home/django/graphite/static/last24h/cs2.py')
            #return returncode
            
        
            return HttpResponseRedirect(reverse('csr',args=[strin])) #reverse('last24h:csresults',args={topic}))#

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()
        form2 = NameForm()
    log_inf, log_link = check_login(request)
    suggestions = Suggest.objects.filter(custom = 'last24h').order_by('distance')[0:15]
    json = 'last24h' + static('last24h/ug_nl_cluster.json')
    tgt = 'last24h' + static('last24h/tgt_cluster.json')
    context = {'json':json,'tgt': tgt, 'suggestions':suggestions,'name':current_name, 'form':form, 'form2':form2,'log_inf':log_inf, 'log_link':log_link}
    return render(request, 'last24h/index_test3.html', context)



@login_required(login_url='/login')
def csresults(request,topic):
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = NameForm(request.POST)
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            topic2 = form.cleaned_data['query_text']
            topics = topic2.split(',')
            for i in range(0, len(topics)):
                topics[i] = topics[i].strip(' ').lower().replace(" ","_").replace("_"," ")
            strin = "AND".join(topics) + '_' + datetime.datetime.now().isoformat()[:13]
            print topics
            if request.user.is_authenticated():
                q = Query(user = User.objects.get(id =request.user.id), query = topic2, time = datetime.datetime.now(), string = strin, url = reverse('csr',args=[strin]))
                q.save()
            sys.argv = ['/home/django/graphite/static/last24h/cs2.py', topics, strin]
            execfile('/home/django/graphite/static/last24h/cs2.py')
            #return returncode
            
        
            return HttpResponseRedirect(reverse('csr',args=[strin])) #reverse('last24h:csresults',args={topic}))#

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()
         
    log_inf, log_link = check_login(request)
    suggestions = Suggest.objects.filter(custom = 'q' + topic).order_by('distance')
    topic_text = topic[:(len(topic)-14)].replace('AND',', ').replace("_"," ")
    context = {'form':form,'suggestions':suggestions,'name':current_name, 'topic':topic,'topic_text':topic_text,'log_inf':log_inf, 'log_link':log_link}
    return render(request, 'last24h/q_result.html', context) #-{'topic': topic})
  
