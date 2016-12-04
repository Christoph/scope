from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class UserProfile(models.Model):
    # TODO: Model should be removed
    user = models.ForeignKey(User, default=None, null=True)
    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField()


class Customer(models.Model):
    name = models.CharField(max_length=200)
    customer_key = models.CharField(max_length=200)
    email = models.EmailField()

    def __unicode__(self):              # __unicode__ on Python 2
        return self.name


class Source(models.Model):
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=200)

    def __unicode__(self):              # __unicode__ on Python 2
        return self.name


class Agent(models.Model):
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=200)

    def __unicode__(self):              # __unicode__ on Python 2
        return self.name


class Article(models.Model):
    source = models.ForeignKey(Source, blank=True, null=True)
    agent = models.ForeignKey(Agent, blank=True, null=True)
    title = models.CharField(max_length=300)
    url = models.CharField(max_length=300)
    images = models.CharField(max_length=500, blank=True)
    description = models.CharField(max_length=500, blank=True)
    keywords = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    # time_written = models.DateTimeField(blank=True)
    time_created = models.DateField(auto_now_add=True)

    def __unicode__(self):              # __unicode__ on Python 2
        return self.title
