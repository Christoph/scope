from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Create your models here.


class Customer(models.Model):
    name = models.CharField(max_length=200)
    customer_key = models.CharField(max_length=200)
    email = models.EmailField()

    def __unicode__(self):              # __unicode__ on Python 2
        return self.name


class UserProfile(models.Model):
    # TODO: Model should be removed
    user = models.ForeignKey(User, default=None, null=True)
    activation_key = models.CharField(max_length=40)
    expires = models.DateTimeField()
    customer = models.ForeignKey(Customer, default=None, null=True)
    def __unicode__(self):              # __unicode__ on Python 2
        return self.user.name


class Agent(models.Model):
    product_customer_type = models.ForeignKey(
        ContentType, related_name="product_customer")
    product_customer_id = models.PositiveIntegerField()
    product_customer_object = GenericForeignKey(
        "product_customer_type", "product_customer_id")

    agent_type = models.ForeignKey(ContentType, related_name="agent_type")
    agent_id = models.PositiveIntegerField()
    agent_object = GenericForeignKey("agent_type", "agent_id")

    def __unicode__(self):              # __unicode__ on Python 2
        return str(self.agent_id) + ', ' + str(self.agent_type)


class Source(models.Model):
    name = models.CharField(max_length = 200, )
    url = models.CharField(max_length=200)
    def __unicode__(self):
        return self.url


class AgentImap(models.Model):
    user = models.CharField(blank=True, max_length=100)
    pwd = models.CharField(blank=True, max_length=100)
    imap = models.CharField(blank=True, max_length=100)
    mailbox = models.CharField(blank=True, max_length=100)
    interval = models.IntegerField(blank=True, default=24)

class AgentEventRegistry(models.Model):
    user = models.CharField(blank=True, max_length=100)
    pwd = models.CharField(blank=True, max_length=100)
    lang = models.CharField(blank=True, max_length=10)
    concepts = models.CharField(blank=True, max_length=200)
    locations = models.CharField(blank=True, max_length=200)

class Article(models.Model):
    source = models.ForeignKey(Source, blank=True, null=True)
    title = models.CharField(max_length=500)
    url = models.CharField(max_length=1000)
    images = models.CharField(max_length=1000, blank=True)
    keywords = models.CharField(max_length=200, blank=True)
    body = models.TextField()
    time_created = models.DateField(auto_now_add=True)

    def __unicode__(self):              # __unicode__ on Python 2
        return self.title
