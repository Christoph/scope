from django.contrib import admin

# Register your models here.
from .models import Customer, Article

admin.site.register(Customer)
admin.site.register(Article)
