
from django.db import models
from django import forms
from django.contrib.auth.models import User
# Create your models here.
    
# Create your models here.
class UserProfile(models.Model):
    user = models.ForeignKey(User, default = None,null = True)
    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField()

class Article(models.Model): #formerly Nodes
    title = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    summary = models.CharField(max_length=200)
    keywords = models.CharField(max_length=200)
    def __unicode__(self):              # __unicode__ on Python 2
        return self.title

# class Customer(models.Model):     
#     title = models.CharField(max_length=200)
#     id = models.IntegerField()
#     def __unicode__(self):              # __unicode__ on Python 2
#         return self.title