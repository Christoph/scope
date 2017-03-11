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
from django.templatetags.static import static
from django.conf import settings


from django import forms
from django.core.mail import send_mail,EmailMessage

from scope.models import Article
from homepage.forms import AlertEditForm,NameForm, AlertForm, RegistrationForm,ContactForm,RegistrationForm2,SourceForm
#from curate.models import Select
from explore.models import Sources, Query
from alert.models import Alert, Send

# from conf.celery import app
from random import randint

from conf.tasks import cs_task, sample_brief


def mobile(request):
    return render(request, 'explore/mobile.html')



def home(request):
    return render(request, 'explore/home.html')



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
    context = {'user_id':user_id, 'existingfeed':existingfeed,'form':form,'form2':form2}
    return render(request, 'explore/custom_search.html', context)


#@login_required(login_url='/login')
def custom_results(request,strin):
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
    try:
        info = Query.objects.filter(string = strin)[0]
    except:
        info = ""
    context = {'term':term, 'info':info,'strin':strin, 'time':time,'query':query}
    return render(request, 'explore/custom_results.html', context) #-{'topic': topic})



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



#@login_required(login_url='/login')
def alert(request):
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
    return render(request, 'explore/alert.html',{'existingfeed':existingfeed,'state':state, 'form': form,'form2':form2})
