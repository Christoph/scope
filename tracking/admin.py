from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Curate_Open_Event)
admin.site.register(Curate_Click_Event)
admin.site.register(Source_Click_Event)
