# from __future__ import unicode_literals

from django.db import models
from scope.models import Article, Customer, Agent, Source, Newsletter

# Create your models here.

class Curate_Customer(models.Model):
    customer = models.ForeignKey(Customer)
    key = models.CharField(max_length=100, blank=True)
    expires = models.DateField(blank=True)
    bad_source = models.ManyToManyField(Source, blank=True)

    def __unicode__(self):              # __unicode__ on Python 2
        return self.customer.name


class Curate_Customer_Selection(models.Model):
    curate_customer = models.ForeignKey(Curate_Customer)
    kind = models.CharField(max_length=3, choices=(
        ("sel","selection"),
        ("mis","mistake"),
        ("oth","other"),
        ), default="sel"
        )
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=100, default="#fff")
    def __unicode__(self):              # __unicode__ on Python 2
        return self.name + ', ' + self.curate_customer.customer.name

    def human_readable_name(self):
        return self.name.replace('_', ' ')

class Curate_Rejection_Reasons(models.Model):
    selection = models.ForeignKey(Curate_Customer_Selection, related_name='rejection_reason')
    name = models.CharField(max_length=100)
    kind = models.CharField(max_length=3, choices=(
        ("sou","bad source"),
        ("con","bad content"),
        ("frq","too frequent"),
        ("oth","other")
        ), default="con"
        )
    current_members = models.ManyToManyField('Article_Curate_Query', blank=True, null=True)
    def __unicode__(self):              # __unicode__ on Python 2
        return self.name + ', ' + self.selection.name + ', ' + self.selection.curate_customer.customer.name
    def human_readable_name(self):
        return self.name.replace('_', ' ')

class Curate_Query(models.Model):
    curate_customer = models.ForeignKey(Curate_Customer)
    time_stamp = models.DateField(auto_now_add=True)
    processed_words = models.CharField(max_length=200, blank=True)
    articles_before_filtering = models.IntegerField(null=True, blank=True)
    clustering = models.CharField(max_length=200, blank=True)
    no_clusters = models.IntegerField(null=True, blank=True)
    selection_made = models.BooleanField(default=False)

    def __unicode__(self):              # __unicode__ on Python 2
        return self.time_stamp.isoformat() + ', ' + self.curate_customer.customer.name


class Article_Curate_Query(models.Model):
    rank = models.IntegerField(null=True, blank=True)
    cluster_label = models.IntegerField(null=True, blank=True)
    article = models.ForeignKey(Article)
    curate_query = models.ForeignKey(Curate_Query)
    #keywords = models.CharField(max_length=50)
    selection_options = models.ManyToManyField(Curate_Customer_Selection, blank=True)
    agent = models.ForeignKey(Agent, null=True, blank=True)
    newsletter =  models.ForeignKey(Newsletter, null=True, blank=True)
    bad_article = models.BooleanField(default=False)
    def __unicode__(self):              # __unicode__ on Python 2
        return self.article.title + ', ' + self.curate_query.time_stamp.isoformat() + ', ' + self.curate_query.curate_customer.customer.name

class Curate_Query_Cluster(models.Model):
    center = models.ForeignKey(Article_Curate_Query)
    cluster_articles = models.ManyToManyField(Article_Curate_Query, blank=True)




