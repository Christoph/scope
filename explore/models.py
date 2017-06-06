

from django.db import models
from django.contrib.auth.models import User
import django.utils.timezone



class Query(models.Model):
    user = models.ForeignKey(User, default = None,null = True)
    query = models.CharField(max_length=200)
    time = models.DateTimeField(default = django.utils.timezone.now)
    string = models.CharField(max_length=200)
    url = models.CharField(max_length=200)
    articlenumber = models.IntegerField(null = True,blank=True)
    words = models.IntegerField(null = True,blank=True)

class Sources(models.Model):
    name = models.CharField(max_length = 200)
    url = models.CharField(max_length=200)
    def __str__(self):
        return self.name