# from __future__ import unicode_literals

from django.db import models
from scope.models import Article, Customer, Agent

# Create your models here.


class Curate_Customer(models.Model):
    customer = models.ForeignKey(Customer)
    key = models.CharField(max_length=100, blank=True)
    expires = models.DateField(blank=True)


class Curate_Customer_Selection(models.Model):
    curate_customer = models.ForeignKey(Curate_Customer)
    name = models.CharField(max_length=100)

class Curate_Query(models.Model):
    curate_customer = models.ForeignKey(Curate_Customer)
    time_stamp = models.DateField(auto_now_add=True)
    processed_words = models.CharField(max_length=200, blank=True)
    clustering = models.CharField(max_length=200, blank=True)
    no_clusters = models.IntegerField(null=True, blank=True)


class Article_Curate_Query(models.Model):
    is_selected = models.BooleanField(default=False)
    is_mistake = models.BooleanField(default=False)
    rank = models.IntegerField(null=True, blank=True)
    article = models.ForeignKey(Article)
    curate_query = models.ForeignKey(Curate_Query)
    agent = models.ForeignKey(Agent, null=True, blank=True)

class Article_Curate_Query_Selection(models.Model):
    curate_cutomer_seletion = models.ForeignKey(Curate_Customer_Selection)
    article_curate_query = models.ForeignKey(Article_Curate_Query)
    is_true = models.BooleanField(default=False)
