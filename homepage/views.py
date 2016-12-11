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
#from curate.models import Select
from explore.models import Query, Sources
from alert.models import Alert, Send
from scope.models import UserProfile

from time import mktime
from datetime import timedelta
from datetime import datetime, date



def register(request,):
    state = "With a profile you can manage and edit your alerts, access previous search results and unlock other great features!"
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
                    return render(request,'homepage/register.html', {'new':False,'state':state, })
                else:
                    state="Sorry, but this username is already taken."

            else:
                state = "Passwords mismatch, try again."

    else:
        form = RegistrationForm()
    return render(request,'homepage/register.html', {'new':True,'form': form, 'state':state})
            # Save the user
def confirm(request, activation_key):
    if request.user.is_authenticated():
        return render_to_response('homepage/confirm.html', {'has_account': True, })
    user_profile = get_object_or_404(UserProfile,
                                     activation_key=activation_key)
    if user_profile.key_expires.replace(tzinfo = None)  < datetime.today():
        return render_to_response('homepage/confirm.html', {'expired': True, })
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
    return render_to_response('homepage/confirm.html', {'success': True, })

#@login_required(login_url='/login')
def disclaimer(request):
    return render(request,'homepage/disclaimer.html', )

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

    context = {'user':user, 'recent_queries':recent_queries, 'alert_info':alert_info,'state':state,'form2':form2,'state_profile':state_profile}
    return render(request, 'homepage/profile.html', context)

def logout(request):
    logout(request)
    return render(request, 'homepage/logout.html')

    
# def login_user(request):
#     state = ""
#     username = password = ''
#     if request.POST:
#         username = request.POST['username']
#         password = request.POST['password']

#         user = authenticate(username=username, password=password)
#         if user is not None:
#             if user.is_active:
#                 login(request, user)
#                 #state = "You are succesfully logged in. Please proceed to"
#                 #render(request, 'last24h/index.html')
#                 return HttpResponseRedirect(reverse('profile'))
#             # Redirect to a success page.
#             else:
#             # Return a 'disabled account' error message
#                 state = "Your account is not active, please contact the site admin."
#         else:
#         # Return an 'invalid login' error message.
#             state = "Your username and/or password were incorrect."

#     return render(request, 'homepage/auth.html',{'state':state, 'username': username,})

#@login_required(login_url='/login')
def how_it_works(request):
    return render(request, 'homepage/how_it_works.html',)


def server_error(request):
    return render(request,'homepage/500.html')

def profile_delete(request):
    return render(request, 'homepage/profile_delete.html',)

#@login_required(login_url='/login')
def contact(request):

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
            return render(request,'homepage/contact.html', {'state':state, })
        else:
            state = "Oops. Something went wrong with the data. Please double-check and try again."

    return render(request, 'homepage/contact.html',{'form':form,'state':state})

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
    return render(request,'homepage/landing.html')
