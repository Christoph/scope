from django.contrib import admin

# Register your models here.
from .models import Curate_Customer, Curate_Query, Article_Curate_Query

admin.site.register(Curate_Customer)
admin.site.register(Curate_Query)
admin.site.register(Article_Curate_Query)
