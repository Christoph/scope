from __future__ import unicode_literals

from django.db import models

class Select_NH(models.Model):
    timestamp = models.DateField(auto_now_add=True)
    is_selected = models.BooleanField(default=False)
    is_mistake = models.BooleanField(default=False)
    rank = models.IntegerField(null = True,blank=True)#DecimalField(max_digits = 4, decimal_places = 0, null = True, blank = True)
    title = models.CharField(max_length=900)
    url = models.CharField(max_length=900)
    summary = models.CharField(max_length=1000)
    keywords = models.CharField(max_length=900)
    images = models.CharField(max_length=900)
    source = models.CharField(max_length=900)
    #text = models.CharField(max_length=9000)
    def __unicode__(self):              # __unicode__ on Python 2
        return self.title


