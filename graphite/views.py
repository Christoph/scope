from django.shortcuts import render, get_object_or_404, render_to_response
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, AnonymousUser
from last24h.models import Alert, Suggest, Query,UserProfile,Send
from last24h.forms import AlertEditForm,NameForm, AlertForm, RegistrationForm,ContactForm,RegistrationForm2
from django.template import RequestContext, loader
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.db import connections
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render
from django.templatetags.static import static
from django.conf import settings
import random, sha
from django.core.mail import send_mail,EmailMessage

import sys
import threading
import Queue
import time
import datetime

global workQueue, exitFlag, queueLock, current_name

current_name = settings.CURRENT_NAME

exitFlag = 0

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



def check_login(request):
    if request.user.is_authenticated():
        log_inf = ['Profile','Logout']
        log_link = ['profile','logout_user']
    else: 
        log_inf = ['Register','Login']
        log_link = ['register','login_user']
    return log_inf, log_link
    
from random import randint

def martin(request):
    messages = ["'My name is Martin and I will save you', he said.","She shyly looked up on him.","His chin was quite big.","Kazoom!!","Nothing happened.","The wind rose.","'Dontt worry, babe', he said","They walked down the road","Godzilla","She cried","He cried","A tear dropped on the floow","'I hate you', she said", "He pressed her tightly against him"]
    state = "Go for it, birthday boy!"
    if request.method == 'POST':
        if 'add' in request.POST:            
            state = messages[randint(0,len(messages)-1)]
        if 'reset' in request.POST:
            state = "hit me, Martin!"
#	if 'append' in request.POST:
#	    messages.appendrequest.POST['text']
    return render(request,'graphite/martin.html', {'state': state})
  



def artsy(request):
    return render(request, 'graphite/artsy_rects_upon_suggest.html') #-{'topic': topic})

def register(request,):
    state = "Register here for a profile with us to access more grews features!"
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
                    key_expires = datetime.datetime.today() + datetime.timedelta(2)
            
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
                    return render(request,'graphite/register.html', {'state':state, 'log_inf':log_inf, 'log_link':log_link})
                else: 
                    state="Sorry, but this username is already taken."
                    
            else: 
                state = "Passwords mistmatch, try again."
               
    else:
        form = RegistrationForm() 
    return render(request,'graphite/register.html', {'name':current_name,'form': form.as_p(), 'state':state, 'log_inf':log_inf, 'log_link':log_link})
            # Save the user                                                                                                                                                 
def confirm(request, activation_key):
    log_inf, log_link = check_login(request)
    if request.user.is_authenticated():
        return render_to_response('graphite/confirm.html', {'name':current_name,'has_account': True, 'log_inf':log_inf, 'log_link':log_link})
    user_profile = get_object_or_404(UserProfile,
                                     activation_key=activation_key)
    if user_profile.key_expires.replace(tzinfo = None)  < datetime.datetime.today():
        return render_to_response('graphite/confirm.html', {'name':current_name,'expired': True, 'log_inf':log_inf, 'log_link':log_link})
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
    return render_to_response('graphite/confirm.html', {'success': True,'name':current_name, 'log_inf':log_inf, 'log_link':log_link})

@login_required(login_url='/login')
def disclaimer(request):
    log_inf, log_link = check_login(request)    
    return render(request,'graphite/disclaimer.html', {'log_inf':log_inf, 'log_link':log_link,'name':current_name})

@login_required(login_url='/login')
def about(request):
    log_inf, log_link = check_login(request)    
    return render(request,'graphite/about.html', {'log_inf':log_inf, 'log_link':log_link,'name':current_name})

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
        print request.POST
        if 'save' in request.POST:
            q = Alert.objects.get(no=request.POST['no'])
            q.query = request.POST['query']
            q.frequency = request.POST['frequency']
            try: q.save()
            except: state = "It seems there is a problem with the data you entered. Please try and correct"
            return HttpResponseRedirect(reverse('profile'))
        elif 'delete' in request.POST:
            q = Alert.objects.get(no = request.POST['no'])
            state = 'The alert "' + q.query + '" was successfully deleted.'           
            q.delete()
            alerts2 = Alert.objects.filter(user = user).order_by('delivery_time')
            for i in range(0,len(alerts)):
                alert.no = str(user.id) + '_' + str(i)
                
            return HttpResponseRedirect(reverse('profile'))
        elif 'save_profile' in request.POST:
            
            user.first_name = request.POST['first']
            user.last_name = request.POST['last']
            user.username = request.POST['username']
            user.email = request.POST['email']
                
            user.save()
            state_profile = "Changes have been saved"
            form2 = RegistrationForm2(request.POST)
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
            alert_info.append((alerts[i], AlertEditForm(initial = {'query' : alerts[i].query, 'frequency' : alerts[i].frequency, 'no' : alerts[i].no }).as_p()))
    recent_queries = Query.objects.filter(user = user).order_by('time')[:10]
    suggestions = []
    for query in recent_queries:
        csstring = 'cs' + query.string
        suggestions.append(Suggest.objects.filter(custom = csstring).order_by('distance')[:2])
    
    context = {'suggestions':suggestions,'name':current_name, 'user':user, 'recent_queries':recent_queries, 'alert_info':alert_info, 'log_inf':log_inf, 'log_link':log_link, 'state':state,'form2':form2.as_p(),'state_profile':state_profile}
    return render(request, 'graphite/profile.html', context)


def logout_user(request):
    logout(request)
    return render(request, 'graphite/logout.html',{'name':current_name,'log_inf': ['Register','Login'],'log_link': ['register','login_user']})

def login_user(request):
    state = "Please log in below..."
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
                return HttpResponseRedirect(reverse('last24h:index')) 
            # Redirect to a success page.
            else:
            # Return a 'disabled account' error message
                state = "Your account is not active, please contact the site admin."
        else:
        # Return an 'invalid login' error message.
            state = "Your username and/or password were incorrect."
    log_inf, log_link = check_login(request)
    
    return render(request, 'graphite/auth.html',{'name':current_name,'state':state, 'username': username,'log_inf':log_inf, 'log_link':log_link})


@login_required(login_url='/login')
def about(request):
    log_inf, log_link = check_login(request)
    return render(request, 'graphite/about.html',{'name':current_name,'log_inf':log_inf, 'log_link':log_link})

@login_required(login_url='/login')
def how_it_works(request):
    log_inf, log_link = check_login(request)
    return render(request, 'graphite/how_it_works.html',{'name':current_name,'log_inf':log_inf, 'log_link':log_link})

@login_required(login_url='/login')
def customsearch(request):     
        # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form2 = NameForm(request.POST)
        # check whether it's valid:
        if form2.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            topic = form2.cleaned_data['query_text']
            topics = topic.split(',')
            for i in range(0, len(topics)):
                topics[i] = topics[i].strip(' ').lower().replace(" ","_")
            strin = "AND".join(topics) + '_' + datetime.datetime.now().isoformat()[:13]
            print topics
            if request.user.is_authenticated():
                q = Query(user = User.objects.get(id =request.user.id), query = topic, time = datetime.datetime.now(), string = strin, url = reverse('csr',args=[strin]))
                q.save()
            sys.argv = ['/home/django/graphite/static/last24h/cs.py', topics, strin]
            #return returncode
            execfile('/home/django/graphite/static/last24h/cs.py')
            return HttpResponseRedirect(reverse('csr',args=[strin])) #reverse('last24h:csresults',args={topic}))#
    # if a GET (or any other method) we'll create a blank form
    else:
        form2 = NameForm()
    #suggest = Suggest.objects.order_by('id')[:15]
    log_inf, log_link = check_login(request)
    context = {'form':form2, 'log_inf':log_inf, 'log_link':log_link,'name':current_name}
    return render(request, 'graphite/custom_search.html', context)  


@login_required(login_url='/login')
def csr(request,strin):
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
            sys.argv = ['/home/django/graphite/static/last24h/cs.py', topics, strin]
            execfile('/home/django/graphite/static/last24h/cs.py')
            #return returncode
            
        
            return HttpResponseRedirect(reverse('csr',args=[strin])) #reverse('last24h:csresults',args={topic}))#

    # if a GET (or any other method) we'll create a blank form
    else:
        form = NameForm()
    log_inf, log_link = check_login(request)
    topic_text = strin[:(len(strin)-14)].replace('AND',', ').replace("_"," ")
    suggestions = Suggest.objects.filter(custom = 'cs' + strin).order_by('distance')
    context = {'form': form, 'suggestions':suggestions, 'strin':strin,'topic_text':topic_text,'name':current_name, 'log_inf':log_inf, 'log_link':log_link}
    return render(request, 'graphite/cs_result.html', context) #-{'topic': topic})


@login_required(login_url='/login')
def grews_alert(request):
    state = "Please specify your alert parameters..."
    if request.method == 'POST':
        if request.user.is_authenticated():
            form = AlertForm(request.POST, initial = {'email': request.user.email})
        else: 
            form = AlertForm(request.POST)
        
        if request.POST:
            
            if form.is_valid():
                email = form.cleaned_data['email']
                frequency = form.cleaned_data['frequency']       
                delivery_time = form.cleaned_data['delivery_time']
                query = form.cleaned_data['query']
                
                #copies = form.cleaned_data['copies']
                if request.user.is_authenticated():
                    user = User.objects.get(id=request.user.id)
                    try:
                        user_alert = Alert.objects.filter(user=user)
                    except:
                        user_alert = []
                    
                    no = str(user.id) + '_' + str(len(user_alert) + 1)
                    q = Alert(email = email, frequency = frequency, delivery_time = delivery_time, query = query, user = user,no = no)
                else:
                    q = Alert(email = email, frequency = frequency, delivery_time = delivery_time, query = query)#copies = copies

                q.save()
                
                state = "Congratulations. Now look forward to your first grews-alert in your inbox." 
                form = AlertForm()
                # Redirect to a success page.
            else:
                state = "It seems there is a problem with the data you entered. Please try and correct"
                form.errors
    else:     
        if request.user.is_authenticated():
            form = AlertForm(initial = {'email': request.user.email})
        else: 
            form = AlertForm()
    log_inf, log_link = check_login(request)
    return render(request, 'graphite/set_alert.html',{'state':state, 'form': form.as_p(),'log_inf':log_inf,'name':current_name, 'log_link':log_link})

def profile_delete(request):
    log_inf, log_link = check_login(request)
    return render(request, 'graphite/profile_delete.html',{'log_inf':log_inf, 'log_link':log_link,'name':current_name})

@login_required(login_url='/login')
def contact(request):
    log_inf, log_link = check_login(request)
    state = "Please drop us any feedback or suggestions or simply get in touch with us!"
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
        
    return render(request, 'graphite/contact.html',{'log_inf':log_inf, 'log_link':log_link, 'form':form.as_p(),'name':current_name,'state':state})




