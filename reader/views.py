# Create your views here.
import feedparser
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.forms import modelform_factory
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings
from datetime import timedelta
from datetime import datetime


from .models import User_Reader, RSSFeed, Reader_Query, Reader_Query_Cluster, Article_Reader_Query
from .forms import ReaderForm, SourceForm
from scope.models import UserProfile
from homepage.forms import RegistrationForm


def register(request):
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
				print(request.POST['username'])

				if form.isValidUsername(request.POST['username']):
			# process the data in form.cleaned_data as required
			# ...
			# redirect to a new URL:
					print()
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
					print('render created')
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


@login_required()
def interface(request,username=None, date_stamp=None):
	try:
		if username == None or request.user.is_superuser and username == request.user.username:
			user_reader = User_Reader.objects.get(user=request.user)

	except:
		return redirect('/login/?next=%s' % request.path)
	
	print("passed")
	if date_stamp==None:
		query = Reader_Query.objects.filter(user_reader=user_reader).order_by("pk").last()
	else:
		date_parsed = datetime.strptime(date_stamp,'%d%m%Y').date()
		query = Reader_Query.objects.filter(user_reader=user_reader).filter(time_stamp=date_parsed).order_by("pk").last()
	suggestions = Reader_Query_Cluster.objects.filter(
			center__reader_query=query).order_by('rank')
	#suggestions = Article_Curate_Query.objects.filter(curate_query=query).filter(rank__gt = 0).order_by("rank")
	#suggestions = [cluster.center for cluster in clusters]
	# options = Curate_Customer_Selection.objects.filter(curate_customer=curate_customer).order_by("pk")
	# if request.method == 'POST':
	# 	config = configparser.RawConfigParser()
	# 	config.read('curate/customers/' + key +
	# 					 "/" + key + '.cfg')
	# 	query.selection_made = True
	# 	query.save()
	# 	selected_articles = []
	# 	for i in range(1, len(suggestions) + 1):
	# 		for option in options:                    
	# 			try:
	# 				xx = request.POST[option.name + str(i)]
	# 				if xx == 'on':
	# 					s = suggestions[i-1]
	# 					selected_articles.append({"title": s.center.article.title, "body": s.center.article.body[0:200], "selection": option.name})
	# 					for reason in option.rejection_reason.all():
	# 						try:
	# 							yy = request.POST[option.name + str(i) + reason.name]
	# 							print(yy)
	# 							if  yy == "on":
	# 								if reason.kind == "sou":
	# 									curate_customer.bad_source.add(s.center.article.source)
	# 									curate_customer.save()
	# 								else:
	# 									reason.current_members.add(s.center)
	# 									reason.save()
	# 									if reason.kind == "con":
	# 										s.center.bad_article = True
	# 						except:
	# 							pass
	# 					s.center.selection_options.add(option)
	# 					s.center.save()
	# 			except:
	# 				pass
					
	# 	try:
	# 		selection_made_task(key, selected_articles)
	# 		selection_made_task.delay(key, selected_articles)
	# 	except:
	# 		pass
	# 	try:
	# 		print(im.get_env_variable('DJANGO_SETTINGS_MODULE'))
	# 		#print(config.getboolean('meta','direct_outlet'))
	# 		if im.get_env_variable('DJANGO_SETTINGS_MODULE') == "conf.settings.deployment": #and not request.user.is_superuser:
	# 			send_newsletter_task.delay(key)
	# 	except:
	# 		print('Problem with sending the mail to others')
	# 		pass

	# stats = {}
	# for option in options.all():
	# 	stat = [i for i in suggestions if option in i.center.selection_options.all()]
	# 	stats[option] = len(stat)
	# print(suggestions, query)
	context = {"suggestions": suggestions, 'query': query, 'username': request.user.username}
	return render(request, 'reader/reader.html', context)

@login_required(login_url='/login')
def profile(request):
	#on this pager there should be the personal info and a selection of feeds, nothing else.
	#three forms: change personal information, change selection, add feed
	UserForm = modelform_factory(User, fields="__all__")
	Readerform = modelform_factory(User_Reader, fields=('feeds', 'no_output_articles'), form= ReaderForm)
	readerform = Readerform(instance=request.user)
	userform = UserForm(instance=request.user)
	sourceform = SourceForm()
	existingfeed = 0
	print(request.POST)
	if request.method == 'POST':
		if 'change_reader' in request.POST:
			readerformset = Readerform(request.POST)
			if readerformset.is_valid():
				readerformset.save()

		if 'change_user' in request.POST:
			userformset = UserForm(request.POST)
			if userformset.is_valid():
				userformset.save()
			else: 
				print("not valid")

		if 'add_feed' in request.POST:
			if len(feedparser.parse(request.POST['url'])['entries']) != 0:
				new_feed, created = RSSFeed.objects.get_or_create(url=request.POST['url'], defaults={'name':request.POST['name']})
				if not created:
					existingfeed = 1
				else: 
					return HttpResponseRedirect(reverse('reader:profile'))
			else:
				existingfeed = 2

		if 'delete_profile' in request.POST:
			try:
				#you should do a cascade here for all queries related to that user...
				User_Reader.objects.get(user=request.user).delete()
			except:
				None
				#delete the alerts, all the Suggest objects for each of the graphs that have been produced, and all the. No. delete suggestions and graph data otherwise through schedule24h. Specifically, check whether there exist graphs/suggest/query objects whose latest url is not the url of any alert or query.(be careful with "recent queries") if not, delete them. But don't delete them when deleting a user (if you delete the user, then this will show up with the next check
			logout(request)
			request.user.delete()
			return HttpResponseRedirect(reverse('reader:profile_delete'))

	return render(request, 'reader/profile.html',{'existingfeed':existingfeed, 'sourceform': sourceform, 'userform': userform,'readerform':readerform})

def profile_delete(request):
	return render(request, 'reader/profile_delete.html',)

