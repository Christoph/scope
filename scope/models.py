
from django.db import models
from django import forms
from django.contrib.auth.models import User
# Create your models here.
    
# Create your models here.
class UserProfile(models.Model):
    user = models.ForeignKey(User, default = None,null = True)
    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField()
    #customer = models.CharField(max_length=200,blank=True)foreign keys

class Article(models.Model): #formerly Nodes
    title = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    images = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    keywords = models.CharField(max_length=200)
    body = models.CharField(max_length=20000)
    time_written = models.DateTimeField()
    time_created = models.DateField(auto_now_add=True)
    #sources = models.Many-to-many(Source) 
    #agents = models.Many-to-many(Agent)
    def __unicode__(self):              # __unicode__ on Python 2
        return self.title

class Customer(models.Model):     
    name = models.CharField(max_length=200)
    customer_id = models.CharField(max_length=200)
    email = models.EmailField()
    def __unicode__(self):              # __unicode__ on Python 2
        return self.name

class Query(models.Model):     
    customer_id = models.CharField(max_length=200)
    time_stamp = models.DateField(auto_now_add=True)
    processed_words = models.CharField(max_length=200)
    clustering = models.CharField(max_length=200)  #this and other global information that isn't implicity from the article or app_query models
    def __unicode__(self):              # __unicode__ on Python 2
        return self.time_stamp


# class Source(models.Model):     
#     name = models.CharField(max_length=200)
#     used_by_customer = models.CharField(max_length=200) # Foreign Field one-to-many, meant to capture which customers use what channels and resources
#     url = models.CharField(max_length=200)
#     def __unicode__(self):              # __unicode__ on Python 2
#         return self.name

# class Agent(models.Model):     
#     name = models.CharField(max_length=200)
#     url = models.CharField(max_length=200)
#     def __unicode__(self):              # __unicode__ on Python 2
#         return self.name

