from django.shortcuts import render, get_object_or_404, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, AnonymousUser


from django.template import RequestContext, loader
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.db import connections
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render
from django.templatetags.static import static
from django.conf import settings
from django import forms
from django.core.mail import send_mail,EmailMessage

from scope.models import Article
from homepage.forms import AlertEditForm,NameForm, AlertForm, RegistrationForm,ContactForm,RegistrationForm2,SourceForm
from curate.models import Select
from explore.models import Query, Sources,UserProfile
from alert.models import Alert, Send

import random, sha
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
import Queue
import threading
import time
import untangle
import sys
import json
import urllib
import math
from time import mktime
from datetime import timedelta
from datetime import datetime, date

#from celery import *

from conf.celery import app

#from celery import shared_task, current_task
#from celery.result import * #AsyncResult
#from django.utils import simplejson as json


#from django.views.decorators.csrf import csrf_exempt

from conf.tasks import cs_task, sample_brief, twitter_job

global workQueue, exitFlag, queueLock, current_name, articlenumber

current_name = settings.CURRENT_NAME
#current_domain = settings.CURRENT_DOMAIN

#source_list = [(i.url,i.name) for i in Sources.objects.all()]


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
        current_task.update_state(state='DOWNLOAD',
        meta={'current': 10 + int(counter/articlenumber)*50, 'articles':articlenumber, 'words':0})
        counter += 1
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

def check_login(request):
    if request.user.is_authenticated():
        log_inf = ['Profile','Logout']
        log_link = ['profile','logout_user']
    else: 
        log_inf = ['Register','Login']
        log_link = ['register','login_user']
    return log_inf, log_link
    
from random import randint




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
    suggestions = Select.objects.filter(custom = 'last24h').order_by('distance')[0:15]
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
    suggestions = Select.objects.filter(custom = 'q' + topic).order_by('distance')
    topic_text = topic[:(len(topic)-14)].replace('AND',', ').replace("_"," ")
    context = {'form':form,'suggestions':suggestions,'name':current_name, 'topic':topic,'topic_text':topic_text,'log_inf':log_inf, 'log_link':log_link}
    return render(request, 'last24h/q_result.html', context) #-{'topic': topic})




def mobile(request):
    log_inf, log_link = check_login(request)
    context = {'log_inf':log_inf, 'log_link':log_link}
    return render(request, 'graphite/mobile.html',context)



def martin(request):
    messages = ["'My name is Martin and I will save you', he said.","She shyly looked up on him.","His chin was quite big.","Kazoom!!","Nothing happened.","The wind rose.","'Dontt worry, babe', he said","They walked down the road","Godzilla","She cried","He cried","A tear dropped on the floow","'I hate you', she said", "He pressed her tightly against him"]
    state = "Go for it, birthday boy!"
    if request.method == 'POST':
        if 'add' in request.POST:            
            state = messages[randint(0,len(messages)-1)]
        if 'reset' in request.POST:
            state = "hit me, Martin!"
#   if 'append' in request.POST:
#       messages.appendrequest.POST['text']
    return render(request,'graphite/martin.html', {'state': state})
  



def artsy(request):
    return render(request, 'graphite/artsy_rects_upon_suggest.html') #-{'topic': topic})

def register(request,):
    state = "With a profile you can manage and edit your alerts, access previous search results and unlock other great features!"
    log_inf, log_link = check_login(request) 
    if request.user.is_authenticated():
        # They already have an account; don't let them register again
        state = "Seems like we already have an account for those details. If you want to create a separate account, please log out from your current account."
    
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = RegistrationForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            if request.POST['password1'] == request.POST['password2']:
                print request.POST['username']
                
                if form.isValidUsername(request.POST['username']):
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
                    print 
                    new_data = request.POST.copy()
                    new_user = form.save(new_data)
            
            # Build the activation key for their account                                                                                                                    
                    salt = sha.new(str(random.random())).hexdigest()[:5]
                    activation_key = sha.new(salt+new_user.username).hexdigest()
                    key_expires = datetime.today() + timedelta(2)
            
                # Create and save their profile                                                                                                                                 
                    new_profile = UserProfile(user=new_user,
                                      activation_key=activation_key,
                                      key_expires=key_expires)
                    new_profile.save()
            
            # Send an email with the confirmation link                                                                                                                      
                    email_subject = 'Your new Grews profile confirmation'
                    email_body = "Hello, %s, and thanks for creating a Grews profile!\n\nTo activate your account, click this link within 48 hours:\n\n %s/confirm/%s" % (
                    new_user.username,
            settings.CURRENT_DOMAIN,
                    new_profile.activation_key)
                    email_body2 = "Username: %s \n First: %s \n Last: %s \n Mail: %s" %(
                    new_user.username,
                    new_user.first_name,
                        new_user.last_name,
                        new_user.email
                   )
                    send_mail(email_subject,
                          email_body,'grphtcontact@gmail.com',
                         [new_user.email])
                    send_mail('new user registration',
                          email_body2,'grphtcontact@gmail.com',
                         ['grphtcontact@gmail.com'])
                    print 'render created'
                    state="Great! Only one step to go. We've sent you an email with a confirmation link. Please confirm and you're set to go."
                    return render(request,'graphite/register.html', {'new':False,'state':state, 'log_inf':log_inf, 'log_link':log_link})
                else: 
                    state="Sorry, but this username is already taken."
                    
            else: 
                state = "Passwords mismatch, try again."
               
    else:
        form = RegistrationForm() 
    return render(request,'graphite/register.html', {'new':True,'form': form, 'state':state, 'log_inf':log_inf, 'log_link':log_link})
            # Save the user                                                                                                                                                 
def confirm(request, activation_key):
    log_inf, log_link = check_login(request)
    if request.user.is_authenticated():
        return render_to_response('graphite/confirm.html', {'has_account': True, 'log_inf':log_inf, 'log_link':log_link})
    user_profile = get_object_or_404(UserProfile,
                                     activation_key=activation_key)
    if user_profile.key_expires.replace(tzinfo = None)  < datetime.today():
        return render_to_response('graphite/confirm.html', {'expired': True, 'log_inf':log_inf, 'log_link':log_link})
    user_account = user_profile.user
    user_account.is_active = True
    user_account.save()
    email_body2 = "Username: %s \n First: %s \n Last: %s \n Mail: %s" %(
                    user_account.username,
                    user_account.first_name,
                        user_account.last_name,
                        user_account.email
                   )
    send_mail('new user activation',
                          email_body2,'grphtcontact@gmail.com',
                         ['grphtcontact@gmail.com'])
    return render_to_response('graphite/confirm.html', {'success': True, 'log_inf':log_inf, 'log_link':log_link})

#@login_required(login_url='/login')
def disclaimer(request):
    log_inf, log_link = check_login(request)    
    return render(request,'graphite/disclaimer.html', {'log_inf':log_inf, 'log_link':log_link})

#@login_required(login_url='/login')
def about(request):
    log_inf, log_link = check_login(request)    
    return render(request,'graphite/about.html', {'log_inf':log_inf, 'log_link':log_link})

@login_required(login_url='/login')
def profile_edit(request):
    if request.method == 'POST':
        print request.POST
        user = User.objects.get(id=request.user.id)
        user.first_name = request.POST['first']
        user.last_name = request.POST['last']
        user.username = request.POST['username']
        user.email = request.POST['email']            
        user.save()
        return HttpResponse(
                json.dumps({"success": "Changes have been saved"}),
                content_type="application/json"
            )

    else:
        return HttpResponse(
                json.dumps({"nothing to see": "this isn't happening"}),
                content_type="application/json"
            )

@login_required(login_url='/login')
def alert_edit(request):
    if request.method == 'POST':
        print request.POST
        q = Alert.objects.get(no=request.POST['no'])
        q.query = request.POST['query']
        #freq_dict = {"10400":'4 hours',"31200":'12 hours',"62400":'24 hours',"172800":'2 days',"345600":'4 days',"604800":'1 week'}
        print int(request.POST['frequency'])
        q.frequency = int(request.POST['frequency'])
        print "here"
        q.save()
        try: q.save()
        except: 
            return HttpResponse(
                json.dumps({"error": "There occurred some error during saving. Try again"}),
                content_type="application/json"
            )
        return HttpResponse(
            json.dumps({"success": "Changes have been saved"}),
            content_type="application/json"
            )

    else:
        return HttpResponse(
                json.dumps({"nothing to see": "this isn't happening"}),
                content_type="application/json"
            )


@login_required(login_url='/login')
def profile(request):    
    log_inf, log_link = check_login(request)
    user = User.objects.get(id=request.user.id)
    form2 = RegistrationForm2(initial={'first': user.first_name,
    'last': user.last_name,  
    'username':user.username,
    'email': user.email})
    
    alerts = Alert.objects.filter(user = user).order_by('delivery_time')
    alert_info = []
    state = ""
    state_profile = ""
    if request.method == 'POST':
        #print request.POST
        # if 'save' in request.POST:
        #     print request.POST
        #     q = Alert.objects.get(no=request.POST['no'])
        #     q.query = request.POST['query']
        #     q.frequency = request.POST['frequency']
        #     try: q.save()
        #     except: state = "It seems there is a problem with the data you entered. Please try and correct"
        #     return HttpResponseRedirect(reverse('profile'))

        if 'delete' in request.POST:
            q = Alert.objects.get(no = request.POST['no'])
            state = 'The alert "' + q.query + '" was successfully deleted.'           
            q.delete()
            alerts = Alert.objects.filter(user = user).order_by('delivery_time')
            for i in range(0,len(alerts)):
                alerts[i].no = str(user.id) + '_' + str(i)
                alerts[i].save()
                #return HttpResponseRedirect(reverse('profile'))
        # elif 'save_profile' in request.POST:
            
        #     user.first_name = request.POST['first']
        #     user.last_name = request.POST['last']
        #     user.username = request.POST['username']
        #     user.email = request.POST['email']
                
        #     user.save()
        #     state_profile = "Changes have been saved"
        #     form2 = RegistrationForm2(request.POST)

        elif 'delete_profile' in request.POST:
            try:
                Alert.objects.get(user=user).delete()
            except:
                None
                #delete the alerts, all the Suggest objects for each of the graphs that have been produced, and all the. No. delete suggestions and graph data otherwise through schedule24h. Specifically, check whether there exist graphs/suggest/query objects whose latest url is not the url of any alert or query.(be careful with "recent queries") if not, delete them. But don't delete them when deleting a user (if you delete the user, then this will show up with the next check  
            try:
                Query.objects.get(user=user).delete()
            except:
                None
            
            try:
                Send.objects.get(user=user).delete()
            except:
                None
            logout(request)                
            user.delete()
            
            return HttpResponseRedirect(reverse('profile_delete'))
            
    else:
        for i in range(0, len(alerts)):
            alert_info.append((alerts[i], AlertEditForm(initial = {'query' : alerts[i].query, 'frequency' : alerts[i].frequency, 'no' : alerts[i].no })))
    recent_queries = Query.objects.filter(user = user).order_by('-time')[:10]
    # suggestion = []
    #for query in recent_queries:
    #     csstring = 'cs' + query.string
    #     suggestions.append(Suggest.objects.filter(custom = csstring).order_by('distance')[:2])
    
    context = {'user':user, 'recent_queries':recent_queries, 'alert_info':alert_info, 'log_inf':log_inf, 'log_link':log_link, 'state':state,'form2':form2,'state_profile':state_profile}
    return render(request, 'graphite/profile.html', context)

def mobile(request):
    log_inf, log_link = check_login(request)
    context = {'log_inf':log_inf, 'log_link':log_link}
    return render(request, 'graphite/mobile.html',context)

def logout_user(request):
    logout(request)
    return render(request, 'graphite/logout.html',{'log_inf': ['Register','Login'],'log_link': ['register','login_user']})

def login_user(request):
    state = ""
    username = password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
    
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                #state = "You are succesfully logged in. Please proceed to"
                #render(request, 'last24h/index.html')
                return HttpResponseRedirect(reverse('profile')) 
            # Redirect to a success page.
            else:
            # Return a 'disabled account' error message
                state = "Your account is not active, please contact the site admin."
        else:
        # Return an 'invalid login' error message.
            state = "Your username and/or password were incorrect."
    log_inf, log_link = check_login(request)
    
    return render(request, 'graphite/auth.html',{'state':state, 'username': username,'log_inf':log_inf, 'log_link':log_link})


#@login_required(login_url='/login')
def about(request):
    log_inf, log_link = check_login(request)
    return render(request, 'graphite/about.html',{'log_inf':log_inf, 'log_link':log_link})

#@login_required(login_url='/login')
def how_it_works(request):
    log_inf, log_link = check_login(request)
    return render(request, 'graphite/how_it_works.html',{'log_inf':log_inf, 'log_link':log_link})


#@csrf_exempt
# def search_state(request):
#     """ A view to report the progress to the user """
#     print request.GET
#     if 'job' in request.GET:
#         job_id = request.GET['job']
#     else:
#         return HttpResponse('No job id given.')

#     job = app.AsyncResult(job_id)
#     data = job.result or job.state
#     log_inf, log_link = check_login(request)
#     return render(request, 'graphite/progress.html',{'progress':data, 'task_id': job_id,'log_inf':log_inf, 'log_link':log_link})#HttpResponse(json.dumps(data),mimetype='application/json')

def twitter_start(request):
    if request.method == 'POST':
        data = 'Fail'
    #job = customsearch.delay()
        inputt = request.POST.get('input')
        
        job = twitter_job.delay(inputt)
        data = '{"job":"' + str(job.id)+ '"}'    
        json_data = json.dumps(data)
        return HttpResponse(json_data,content_type="application/json")
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )


# def twitter_update(request):
#   data = ''
#   if request.method == 'GET':
#       data = Tweet.objects.get(pk=1).hashtag
#       # if 'task_id' in request.GET:
#       #   tweet_job = app.AsyncResult('task_id')
#       #   data = str(tweet_job.result['current'])
#   return HttpResponse(json.dumps(data))

def twitter(request):
    return render(request, 'graphite/twitter.html') #-{'topic': topic})


#@csrf_exempt
def update_state(request):
    data = '  Initializing'
    #print request.GET
    if request.method == 'GET':
        if 'task_id' in request.GET:
            job_id = request.GET['task_id']
            job = app.AsyncResult(job_id)
                    #request.session['task_id'] = job.id
            print job.state
            if job.state == 'PREPARE':
                data = str(job.result['current']) + ' Initializing'
            elif job.state == 'DOWNLOAD':
                data = str(job.result['current']) + 'Downloading and processing ' + str(job.result['articles']) + ' articles'
            elif job.state == 'SCAN':
                data = str(job.result['current']) + 'Scanning and analysing ' + str(job.result['words']) + ' words'
            elif job.state == 'VISUALISE':
                data = str(job.result['current']) + 'Construct visualization'
            elif job.state == 'SUCCESS':
                data = 50
            elif job.state =='FAILURE':
                data = 500
                
                #strin = request.GET['strin']
                #return HttpResponseRedirect(reverse('csr',args=[strin]))
    return HttpResponse(json.dumps(data))


def server_error(request):
    return render(request,'graphite/500.html')

#@csrf_exempt
def search_task_term(request):
    if request.method == 'POST':
        data = 'Fail'
    #job = customsearch.delay()
        user_id = request.POST.get('user_id')
        query = request.POST.get('query_text')
        print request.POST
        print user_id
        topics = query.split(',') 
        for i in range(0, len(topics)):
            topics[i] = topics[i].strip(' ').lower().replace(" ","_")
        feeds = []
        for i in topics:
            feeds.append('http://news.google.co.uk/news/feeds?pz=1&cf=all&ned=en&hl=en&q=' + i + '&output=rss&num=100')
        strin = datetime.now().isoformat()[:13] + "&feeds=none&term=" + "AND".join(topics)
        query = "\n".join(topics)

        if len(Query.objects.filter(string = strin)) != 0:
            if user_id != "None":
                q = Query(user = User.objects.get(id =user_id), query = query, time = datetime.now(), string = strin, url = reverse('csr',args=[strin]))
                q.save()
            else: 
                q = Query(query = query, time = datetime.now(), string = strin, url = reverse('csr',args=[strin]))
                q.save()
            data = '{"job":"exists","strin": "' + str(strin) + '"}'    
            json_data = json.dumps(data)


        else :
            if user_id != "None":
                q = Query(user = User.objects.get(id =user_id), query = query, time = datetime.now(), string = strin, url = reverse('csr',args=[strin]))
                q.save()
            else: 
                q = Query(query = query, time = datetime.now(), string = strin, url = reverse('csr',args=[strin]))
                q.save()
            print strin
            job = cs_task.delay(feeds,strin,0)
            data = '{"job":"' + str(job.id) + '","strin": "' + str(strin) + '"}'    
            json_data = json.dumps(data)

        return HttpResponse(json_data,content_type="application/json")
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )

#@csrf_exempt
def search_task_feeds(request):
    if request.method == 'POST':
        data = 'Fail'
        user_id = request.POST.get('user_id')
        feeds = request.POST.getlist('feeds[]')
        ids = []
        query = []
        for feed in feeds:
            source = Sources.objects.get(url=feed)
            ids.append(str(source.id))
            query.append(source.name)
        query = "\n".join(query)
        strin = datetime.now().isoformat()[:13] + "&feeds=" + "AND".join(ids) + "&term=none"
        if user_id != "None":
            q = Query(user = User.objects.get(id = user_id), query = query, time = datetime.now(), string = strin, url = reverse('csr',args=[strin]))
            q.save()
        else: 
            q = Query(query = query, time = datetime.now(), string = strin, url = reverse('csr',args=[strin]))
            q.save()
            
        job = cs_task.delay(feeds,strin,0)
        data = '{"job":"' + str(job.id) + '","strin": "' + str(strin) + '"}'    
          #request.session['task_id'] = job.id
        json_data = json.dumps(data)

        return HttpResponse(json_data,content_type="application/json")
    else:
        return HttpResponse(
                json.dumps({"nothing to see": "this isn't happening"}),
                content_type="application/json"
            )


#@login_required(login_url='/login')
def customsearch(request):     
    existingfeed = 0
    if request.user.is_authenticated():
        user_id = request.user.id
    else:
        user_id = None
        # if this is a POST request we need to process the form data
    if request.method == 'POST':
    #     print request.POST
    #     # create a form instance and populate it with data from the request:
    #     if 'search1' in request.POST:
    #         print "hurray"
    #         form2 = NameForm(request.POST)
    #         job = do_work.delay()
            #request.session['task_id'] = job.id
            #return HttpResponseRedirect(reverse('search_state') + '?job=' + job.id)
            
        # check whether it's valid:
        #     if form2.is_valid():
        #         # process the data in form.cleaned_data as required
        #         # ...
        #         # redirect to a new URL:
        #         topic = form2.cleaned_data['query_text']
        #         print topic
        #         topics = topic.split(',') 
        #         for i in range(0, len(topics)):
        #             topics[i] = topics[i].strip(' ').lower().replace(" ","_")
        #         feeds = []
        #         for i in topics:
        #             feeds.append('http://news.google.co.uk/news/feeds?pz=1&cf=all&ned=en&hl=en&q=' + i + '&output=rss&num=100')
        #         strin = "AND".join(topics) + '_' + datetime.now().isoformat()[:13]

        #         print feeds
        #         if request.user.is_authenticated():
        #             q = Query(user = User.objects.get(id =request.user.id), query = topic, time = datetime.now(), string = strin, url = reverse('csr',args=[strin]))
        #             q.save()
        #         sys.argv = ['last24h' + static('last24h/cs2.py'), feeds, strin]
        #         #return returncode
        #         execfile('last24h' + static('last24h/cs2.py'))#'/home/django/graphite/static/last24h/cs2.py')
        #         return HttpResponseRedirect(reverse('csr',args=[strin])) #reverse('last24h:csresults',args={topic}))#
        #     else: 
        #         print "nonon"
        # if 'search2' in request.POST:            
        #     form2 = NameForm(request.POST)
        # # check whether it's valid:
        #     if form2.is_valid():
        #         # process the data in form.cleaned_data as required
        #         # ...
        #         # redirect to a new URL:
        #         feeds = form2.cleaned_data['sources']
        #         print feeds
        #         query_type = 'choice of ' + str(len(feeds)) + ' feeds'
        #         ids = []
        #         for feed in feeds:
        #             ids.append(str(Sources.objects.get(url=feed).id))
        #         strin = "AND".join(ids) + '_' + datetime.now().isoformat()[:13]
                
        #         if request.user.is_authenticated():
        #             q = Query(user = User.objects.get(id =request.user.id), query = query_type, time = datetime.now(), string = strin, url = reverse('csr',args=[strin]))
        #             q.save()
        #         sys.argv = ['last24h' + static('last24h/cs2.py'), feeds, strin]
        #         #return returncode
        #         execfile('last24h' + static('last24h/cs2.py'))#'/home/django/graphite/static/last24h/cs2.py')
        #         return HttpResponseRedirect(reverse('csr',args=[strin])) #reverse('last24h:csresults',args={topic}))#
        if 'add_source' in request.POST:
            if len(Sources.objects.filter(url=request.POST['url'])) == 0:
                if len(feedparser.parse(request.POST['url'])['entries']) != 0:
                    SourceForm(request.POST).save()
                    return HttpResponseRedirect(reverse('customsearch'))    
                else: 
                    existingfeed = 2
                
            else:
                existingfeed = 1
                

            


    # if a GET (or any other method) we'll create a blank form
    form2 = NameForm()#initial = {'sources':source_list})
    #suggest = Suggest.objects.order_by('id')[:15]
    form = SourceForm()
    log_inf, log_link = check_login(request)
    context = {'user_id':user_id, 'existingfeed':existingfeed,'form':form,'form2':form2, 'log_inf':log_inf, 'log_link':log_link}
    return render(request, 'graphite/custom_search.html', context)  


#@login_required(login_url='/login')
def custom_results(request,strin):
    # if request.method == 'POST':
    #     # create a form instance and populate it with data from the request:
    #     form = NameForm(request.POST)
    #     if form.is_valid():
    #         # process the data in form.cleaned_data as required
    #         # ...
    #         # redirect to a new URL:
    #         topic2 = form.cleaned_data['query_text']
    #         topics = topic2.split(',')
    #         for i in range(0, len(topics)):
    #             topics[i] = topics[i].strip(' ').lower().replace(" ","_").replace("_"," ")
    #         strin = "AND".join(topics) + '_' + datetime.now().isoformat()[:13]
    #         print topics
    #         if request.user.is_authenticated():
    #             q = Query(user = User.objects.get(id =request.user.id), query = topic2, time = datetime.now(), string = strin, url = reverse('csr',args=[strin]))
    #             q.save()
    #         sys.argv = [static('last24h/cs2.py'),topics,strin]#'/home/django/graphite/static/last24h/cs2.py', topics, strin]
    #         execfile(static('last24h/cs2.py'))#'/home/django/graphite/static/last24h/cs2.py')
    #         #return returncode
            
        
    #         return HttpResponseRedirect(reverse('csr',args=[strin])) #reverse('last24h:csresults',args={topic}))#

    # # if a GET (or any other method) we'll create a blank form
    # else:
    #     form = NameForm()
    triple = [strin.split('&feeds=')[0],strin.split('&feeds=')[1].split('&term=')[0],strin.split('&feeds=')[1].split('&term=')[1]]
    time = triple[0][5:7] + '/' + triple[0][8:10] + ' ' + triple[0][11:16]
    if triple[1] == 'none':  
        query = [i.title() for i in triple[2].split('AND')]#.append() = ",".join([i.title() for i in triple[2].split('AND')])
        term = True
    else:
        ids = triple[1].split('AND')
        term = False
        query = []
        for i in ids:
            query.append(Sources.objects.get(id = i).name) #query + Sources.objects.get(id = i).name
        
    #form = NameForm()
    log_inf, log_link = check_login(request)
    #topic_text = strin[:(len(strin)-14)].replace('AND',', ').replace("_"," ")
    #query = Query.objects.filter(string = 'strin')
    try:
        info = Query.objects.filter(string = strin)[0]
    except: 
        info = ""
    context = {'term':term, 'info':info,'strin':strin, 'time':time,'query':query, 'log_inf':log_inf, 'log_link':log_link}
    return render(request, 'graphite/custom_results.html', context) #-{'topic': topic})

#@login_required(login_url='/login')
def grews_alert(request):
    if request.user.is_authenticated():
        user = User.objects.get(id=request.user.id)
    else: 
        user = None
    state = ""
    existingfeed = 0

    if request.method == 'POST':
        if 'set' in request.POST:
            print request.POST
            form = AlertForm(request.POST)
            if form.is_valid():
                if (len(form.cleaned_data['query']) != 0) and (len(form.cleaned_data['sources']) != 0):
                    state = "Please make sure to only either enter a search term of select feeds"
                    
                else: 
                    if len(form.cleaned_data['query']) != 0:
                        query = form.cleaned_data['query']
                        feed_type = False
                        topics = query.split(',') 
                        for i in range(0, len(topics)):
                            topics[i] = topics[i].strip(' ').lower().replace(" ","_")
                        feeds = []
                        for i in topics:
                            feeds.append('http://news.google.co.uk/news/feeds?pz=1&cf=all&ned=en&hl=en&q=' + i + '&output=rss&num=100')
                        query = ",".join(topics)
                    else: 
                        feed_type = True
                        feeds = form.cleaned_data['sources']
                        ids = []
                        query = []
                        for feed in feeds:
                            source = Sources.objects.get(url=feed)
                            ids.append(str(source.id))
                            query.append(source.name)
                        query = ",".join(query)
                        feeds = ",".join(feeds)

                    #email = form.cleaned_data['email']
                    frequency = form.cleaned_data['frequency']
                    delivery_time = form.cleaned_data['delivery_time']
                    
                    #copies = form.cleaned_data['copies']

                    try:
                        user_alert = Alert.objects.filter(user=user)
                    except:
                        user_alert = []
                        
                    no = str(user.id) + '_' + str(len(user_alert) + 1)
                    q = Alert(feeds = feeds,frequency = frequency, delivery_time = delivery_time, query = query, user = user,no = no,feed_type = feed_type)
                    q.save()
                    
                    state = "Congratulations. Now look forward to your first alert." 
            form = AlertForm()
                # Redirect to a success page.
            
        if 'add_source' in request.POST:
            if len(Sources.objects.filter(url=request.POST['url'])) == 0:
                if len(feedparser.parse(request.POST['url'])['entries']) != 0:
                    SourceForm(request.POST).save()
                    return HttpResponseRedirect(reverse('grews_alert'))    
                else: 
                    existingfeed = 2
                
            else:
                existingfeed = 1
    
    else: form = AlertForm()
    form2 = SourceForm()
    log_inf, log_link = check_login(request)
    return render(request, 'graphite/set_alert.html',{'existingfeed':existingfeed,'state':state, 'form': form,'form2':form2,'log_inf':log_inf,'log_link':log_link})


def profile_delete(request):
    log_inf, log_link = check_login(request)
    return render(request, 'graphite/profile_delete.html',{'log_inf':log_inf, 'log_link':log_link})

#@login_required(login_url='/login')
def contact(request):
    log_inf, log_link = check_login(request)
    state = "Please drop me any feedback or suggestions or simply hit me with any thoughts of your's on the site!"
    if request.user.is_authenticated():
            form = ContactForm(initial = {'contact_email': request.user.email,'contact_name':request.user.first_name + ' ' + request.user.last_name})
    else: 
        form = ContactForm()
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = ContactForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            email = EmailMessage(
                "New contact form submission from " + request.POST['contact_name'],
                request.POST['content'],'',
                ['grphtcontact@gmail.com'],
                reply_to = [request.POST['contact_email']]
            )
            email.send()
            state="Thanks! Your mail has been sent"                                                                                                                
            return render(request,'graphite/contact.html', {'state':state, 'log_inf':log_inf, 'log_link':log_link})
        else:
            state = "Oops. Something went wrong with the data. Please double-check and try again."
        
    return render(request, 'graphite/contact.html',{'log_inf':log_inf, 'log_link':log_link, 'form':form,'state':state})

#@csrf_exempt
def send_sample(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        #try:
        #forms.EmailField().clean(email)
        sample_brief.delay(email)
        #content = ''
        #send_mail('brief','Sorry, this service works only for html-compatible mail clients','grphtcontact@gmail.com',[email],connection=None, html_message=content)
        data = 'done'
        # except: 
        #    data = 'Invalid email address'
        return HttpResponse(data,content_type="application/json")
    else:
        return HttpResponse(
            json.dumps({"nothing to see": "this isn't happening"}),
            content_type="application/json"
        )


def landing(request):
    form = AlertForm()
    log_inf, log_link = check_login(request)
    context = {'log_inf':log_inf, 'log_link':log_link,'form':form}
    return render(request,'graphite/landing.html',context)

def home(request):
    log_inf, log_link = check_login(request)
    context = {'log_inf':log_inf, 'log_link':log_link}
    return render(request, 'graphite/home.html', context)

def lichtenfels(request):
    log_inf, log_link = check_login(request)
    context = {'log_inf':log_inf, 'log_link':log_link}
    #return render(request, 'graphite/home.html', context)
    return render(request, 'presi/presi_first.html',context)


def vw(request):
    log_inf, log_link = check_login(request)
    context = {'log_inf':log_inf, 'log_link':log_link}
    return render(request, 'graphite/vw.html', context)

def vw2(request):
    log_inf, log_link = check_login(request)
    context = {'log_inf':log_inf, 'log_link':log_link}
    return render(request, 'graphite/vw2.html', context)

def pd(request):
    with open('/home/django/graphite/last24h/static/last24h/pd.pdf', 'r') as pdf:
        response = HttpResponse(pdf.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'inline;filename=some_file.pdf'
        return response
    pdf.closed




  
