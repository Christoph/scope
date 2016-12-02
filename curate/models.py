from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Curate_Query(models.Model):
	#article = models.ForeignField(Article) #refer to article
	#query = models.ForeignField(Query)
    is_selected = models.BooleanField(default=False)
    is_mistake = models.BooleanField(default=False)
    rank = models.IntegerField(null = True,blank=True)#DecimalField(max_digits = 4, decimal_places = 0, null = True, blank = True)
