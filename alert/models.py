from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User, AnonymousUser
# Create your models here.
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