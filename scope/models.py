from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Create your models here.


class Customer(models.Model):
    name = models.CharField(max_length=200)
    customer_key = models.CharField(max_length=200)
    email = models.EmailField()

    def __str__(self):              
        return self.name


class UserProfile(models.Model):
    user = models.ForeignKey(User, default=None, null=True)
    activation_key = models.CharField(max_length=40)
    expires = models.DateTimeField()
    customer = models.ForeignKey(Customer, default=None, null=True)
    def __str__(self):              
        return self.user.username


class Agent(models.Model):
    product_customer_type = models.ForeignKey(
        ContentType, related_name="product_customer")
    product_customer_id = models.PositiveIntegerField()
    product_customer_object = GenericForeignKey(
        "product_customer_type", "product_customer_id")

    agent_type = models.ForeignKey(ContentType, related_name="agent_type")
    agent_id = models.PositiveIntegerField()
    agent_object = GenericForeignKey("agent_type", "agent_id")

    def __str__(self):              
        return str(self.product_customer_type.get_object_for_this_type(pk=self.product_customer_id).customer.name) + ', ' + str(self.agent_type)


class Source(models.Model):
    name = models.CharField(max_length = 200)
    url = models.CharField(max_length=200)
    def __str__(self):
        return self.url

class Newsletter(models.Model):
    name = models.CharField(max_length = 200)
    email = models.EmailField()
    def __str__(self):              
        return self.name       

class AgentImap(models.Model):
    user = models.CharField(blank=True, max_length=100)
    pwd = models.CharField(blank=True, max_length=100)
    imap = models.CharField(blank=True, max_length=100)
    mailbox = models.CharField(blank=True, max_length=100)
    interval = models.IntegerField(blank=True, default=24)
    def __str__(self):              
        return str(self.id) + ', ' + self.user

class AgentEventRegistry(models.Model):
    user = models.CharField(blank=True, max_length=100)
    pwd = models.CharField(blank=True, max_length=100)
    lang = models.CharField(blank=True, max_length=10)
    concepts = models.CharField(blank=True, max_length=200)
    locations = models.CharField(blank=True, max_length=200)
    def __str__(self):              
        return str(self.id) + ', ' + self.user

class AgentNewspaper(models.Model):
    url = models.CharField(blank=True, max_length=200)
    def __str__(self):              
        return str(self.id) + ', ' + self.url

class Article(models.Model):
    source = models.ForeignKey(Source, blank=True, null=True)
    title = models.CharField(max_length=500)
    url = models.CharField(max_length=1000)
    images = models.CharField(max_length=1000, blank=True)
    body = models.TextField()
    time_created = models.DateField(auto_now_add=True)
    pubdate = models.DateTimeField(blank=True, null=True)
    sample = models.CharField(max_length=3000, blank=True, null=True)


    def __str__(self):              
        return self.title

class RSSFeed(models.Model):
    """docstring for RSSFeed"""
    name = models.CharField(max_length=200)
    url = models.CharField(max_length=1000)

    def __str__(self):              
        return self.name

