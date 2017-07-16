from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(RSSFeed)
admin.site.register(User_Reader)
admin.site.register(Article_Reader_Query)
admin.site.register(Reader_Query_Cluster)
