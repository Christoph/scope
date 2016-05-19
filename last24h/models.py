from django.db import models
from django import forms
from django.contrib.auth.models import User, AnonymousUser
import django.utils.timezone
# Create your models here.

class UserProfile(models.Model):
    user = models.ForeignKey(User, default = None,null = True)
    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField()

class Query(models.Model):
    user = models.ForeignKey(User, default = None,null = True)
    query = models.CharField(max_length=200)
    time = models.DateTimeField(default = django.utils.timezone.now)
    string = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    articlenumber = models.IntegerField(null = True,blank=True)
    words = models.IntegerField(null = True,blank=True)
    
class Node(models.Model):
    title = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    summary = models.CharField(max_length=200)
    keywords = models.CharField(max_length=200)
    def __unicode__(self):              # __unicode__ on Python 2
        return self.title
    
    
class Suggest(models.Model):
    custom = models.CharField(max_length=200)
    distance = models.IntegerField(null = True,blank=True)#DecimalField(max_digits = 4, decimal_places = 0, null = True, blank = True)
    title = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    summary = models.CharField(max_length=1000)
    keywords = models.CharField(max_length=200)
    images = models.CharField(max_length=200)
    def __unicode__(self):              # __unicode__ on Python 2
        return self.title
    
class Alert(models.Model):
    no = models.CharField(max_length= 200,null=True)
    user = models.ForeignKey(User, default = None,null = True)
    #email = models.EmailField(max_length = 254)
    frequency = models.IntegerField(choices = ((10400, '4 hours'), (31200,'12 hours'),(62400,'24 hours'),(172800,'2 days'),(345600,'4 days'),(604800,'1 week')))
    delivery_time = models.DateTimeField()
    query = models.CharField(max_length=500)
    feed_type = models.BooleanField(default=False)
    copies = models.NullBooleanField()
    latest_url = models.CharField(max_length=200, null = True)
    feeds = models.CharField(max_length=600,null = True)
    
class Send(models.Model):
   # email = models.EmailField(max_length = 254)
    query = models.CharField(max_length=200)
    user = models.ForeignKey(User, default = None,null = True)
    string = models.CharField(max_length=200)

class Sources(models.Model):
    name = models.CharField(max_length = 200)
    url = models.CharField(max_length=200)
    def __unicode__(self):              # __unicode__ on Python 2
        return self.name
