from django.db import models
from curate.models import Curate_Recipient, Curate_Query, Article_Curate_Query
from scope.models import Source

# Create your models here.
class Curate_Open_Event(models.Model):
    recipient = models.ForeignKey(Curate_Recipient, default=None)
    curate_query = models.ForeignKey(Curate_Query, default=None)
    time_opened = models.DateTimeField()

    def __str__(self):              
        return self.recipient.first + "," + self.recipient.curate_customer.customer.name

# Create your models here.
class Curate_Click_Event(models.Model):
    recipient = models.ForeignKey(Curate_Recipient, default=None)
    article_curate_query = models.ForeignKey(Article_Curate_Query, default=None)
    time_opened = models.DateTimeField()

    def __str__(self):              
        return self.recipient.first + "," + self.recipient.curate_customer.customer.name + "," + self.article_curate_query.article.title

# Create your models here.
class Source_Click_Event(models.Model):
    recipient = models.ForeignKey(Curate_Recipient, default=None)
    source = models.ForeignKey(Source, default=None)
    time_opened = models.DateTimeField()
    
    def __str__(self):              
        return self.recipient.first + "," + self.recipient.curate_customer.customer.name + "," + self.source.name
