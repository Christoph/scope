
from django import forms
from django.forms import ModelForm, widgets
from last24h.models import Alert
from datetime import date
import datetime
from captcha.fields import CaptchaField
from django.core import validators
from django.contrib.auth.models import User
from last24h.models import Sources



class ContactForm(forms.Form):
    contact_name = forms.CharField(required=True,label='Name')
    contact_email = forms.EmailField(required=True,label='Email')
    content = forms.CharField(
        required=True,
        widget=forms.Textarea,label='Message'
    )

class RegistrationForm(forms.Form):
    first= forms.CharField(label='First name', max_length=60)
    last= forms.CharField(label='Last name', max_length=60)  
    username=forms.CharField(label='Username', max_length=30)
    email = forms.EmailField(label='Email', max_length=100)
    password1 =forms.CharField(label='Password',max_length=60,widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', max_length=60,widget=forms.PasswordInput)
    captcha = CaptchaField(label = "Prove you're human")
    
    def isValidUsername(self, field_data):
        try:
            User.objects.get(username=field_data)
        except User.DoesNotExist:
            return True
        else: 
            return False
    
    def save(self, new_data):
        if (new_data['first'] != '')and(new_data['last'] != ''):
            u = User.objects.create_user(new_data['username'],
                                     new_data['email'],
                                     new_data['password1'],first_name=new_data['first'],last_name=new_data['last'])
        elif (new_data['first'] != '')and(new_data['last'] == ''):
            u = User.objects.create_user(new_data['username'],
                                     new_data['email'],
                                     new_data['password1'],first_name=new_data['first'])
        elif (new_data['first'] == '')and(new_data['last'] != ''):
            u = User.objects.create_user(new_data['username'],
                                     new_data['email'],
                                     new_data['password1'],last_name=new_data['last'])
        else:    
            u = User.objects.create_user(new_data['username'],
                                     new_data['email'],
                                     new_data['password1'])
        u.is_active = False
        u.save()
        return u
            
class RegistrationForm2(forms.Form):
    first= forms.CharField(label='First name', max_length=60)
    last= forms.CharField(label='Last name', max_length=60)  
    username=forms.CharField(label='Username', max_length=30)
    email = forms.EmailField(label='Email', max_length=30)
     
              
            
class NameForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(NameForm, self).__init__(*args, **kwargs)
        self.fields['sources'].choices = [(i.url,i.name) for i in Sources.objects.all()]
    query_text = forms.CharField(label='Custom Search Term: Graphite performs an independent search for all terms separated by a comma. To perform a single joint search on several terms A and B enter "A+B"', max_length=300, required=False)
    sources = forms.MultipleChoiceField(label= 'Select sources',widget=forms.SelectMultiple(attrs= {'id': 'sources'}),
                                             choices=(), required=False)

class SourceForm(ModelForm):
    class Meta:
        model = Sources
        fields = ['name','url']
        labels = {
            'name': 'Feed name',
            'url': 'Feed url',
        }

class UserForm(forms.Form):
    user_query = forms.CharField(label='Start a custom search', max_length=100)
    
class AlertForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(AlertForm, self).__init__(*args, **kwargs)
        self.fields['sources'].choices = [(i.url,i.name) for i in Sources.objects.all()]
    query = forms.CharField(label = 'Specify the query terms for this alert, separating different queries with a comma',  max_length=500, widget=forms.TextInput(attrs={'size': '60'}),required=False)
    sources = forms.MultipleChoiceField(label= 'Select sources',widget=forms.SelectMultiple(attrs= {'id': 'sources'}),
                                             choices=(), required=False)
    #email = forms.EmailField(label = 'Your email', initial = 'your mail', max_length = 254)
    frequency = forms.ChoiceField(label = 'Set the frequency of the alert', choices = ((10400, '4 hours'), (31200,'12 hours'),(62400,'24 hours'),(172800,'2 days'),(345600,'4 days'),(604800,'1 week')))#(3600,'1 hour'), (7200,'2 hours'),
    #delivery_time = forms.ChoiceField(label = 'Set the time for first delivery (')
    delivery_time = forms.DateTimeField(initial=datetime.datetime.combine(datetime.date.today() + datetime.timedelta(1), datetime.time(8,0)).strftime('%m/%d/%Y %H:%M'), label = 'Fix a date for the first alert in 24h-format (default upcoming morning 08:00)')   
    #copies = forms.BooleanField(label = 'Would you like us to archive  past query result for you in your profile?', required=False)
    captcha = CaptchaField(label = "Prove you're human")
    
class AlertEditForm(forms.Form):
    query = forms.CharField(label = 'Query',  max_length=500, widget=forms.TextInput(attrs={'size': '60'}))
    frequency = forms.ChoiceField(label = 'Frequency', choices = ((10400, '4 hours'), (31200,'12 hours'),(62400,'24 hours'),(172800,'2 days'),(345600,'4 days'),(604800,'1 week')))#(3600,'1 hour'), (7200,'2 hours'),       
    no = forms.CharField(widget=forms.HiddenInput(),max_length=200)
            
        

class PasswordForm(forms.Form):
    old_password = forms.CharField(label='Password',max_length=60,widget=forms.PasswordInput)
    password1 =forms.CharField(label='Password',max_length=60,widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', max_length=60,widget=forms.PasswordInput)

class RetrievePasswordForm(forms.Form):
    old_password = forms.CharField(label='Password',max_length=60,widget=forms.PasswordInput)
    password1 =forms.CharField(label='Password',max_length=60,widget=forms.PasswordInput)
    password2 = forms.CharField(label='Repeat password', max_length=60,widget=forms.PasswordInput)
 
      
