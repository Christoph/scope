from __future__ import unicode_literals

from django.db import models
from scope.models import Article
from scope.models import Customer

# Create your models here.


class Curate_Customer(models.Model):
    customer_id = models.ForeignKey(Customer)
    key = models.CharField(max_length=100)
    expires = models.DateField()

    def __unicode__(self):              # __unicode__ on Python 2
        return self.customer_id


class Curate_Query(models.Model):
    curate_customer_ID = models.ForeignKey(Curate_Customer)
    time_stamp = models.DateField(auto_now_add=True)
    processed_words = models.CharField(max_length=200)
    clustering = models.CharField(max_length=200)

    def __unicode__(self):              # __unicode__ on Python 2
        return self.time_stamp


class Article_Curate_Query(models.Model):
    is_selected = models.BooleanField(default=False)
    rank = models.IntegerField(null=True, blank=True)
    article_ID = models.ForeignKey(Article)
    curate_query_ID = models.ForeignKey(Curate_Query)
