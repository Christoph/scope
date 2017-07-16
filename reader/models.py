from django.db import models
from django.contrib.auth.models import User
from scope.models import Article ,RSSFeed
# Create your models here.

class User_Reader(models.Model):
    user = models.ForeignKey(User, default=None)
    feeds = models.ManyToManyField(RSSFeed, blank=True)
    no_output_articles = models.IntegerField(null=True, blank=True)
    def __str__(self):              
        return self.user.username

class Reader_Query(models.Model):
    user_reader = models.ForeignKey(User_Reader)
    time_stamp = models.DateField(auto_now_add=True)
    processed_words = models.CharField(max_length=200, blank=True)
    articles_before_filtering = models.IntegerField(null=True, blank=True)
    clustering = models.CharField(max_length=200, blank=True)
    no_clusters = models.IntegerField(null=True, blank=True)
    selection_made = models.BooleanField(default=False)
    # upper_bound = models.IntegerField(null=True, blank=True)
    # lower_bound = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.time_stamp.isoformat() + ', ' + self.user_reader.user.username

    def bad_articles(self):
        return self.article_reader_query_set.filter(bad_article = True)

class Article_Reader_Query(models.Model):
    rank = models.IntegerField(null=True, blank=True)
    article = models.ForeignKey(Article)
    reader_query = models.ForeignKey(Reader_Query)
    feed = models.ForeignKey(RSSFeed, blank=True)
    bad_article = models.BooleanField(default=False)
    def __str__(self):
        return self.article.title + ', ' + self.reader_query.time_stamp.isoformat() + ', ' + self.curate_query.curate_customer.customer.name

class Reader_Query_Cluster(models.Model):
    rank = models.IntegerField(null=True, blank=True)
    center = models.ForeignKey(Article_Reader_Query, related_name='center')
    cluster_articles = models.ManyToManyField(Article_Reader_Query, blank=True, related_name='cluster_articles')
    keywords = models.CharField(max_length=50, blank=True)
    summary = models.CharField(max_length=500, blank=True)
