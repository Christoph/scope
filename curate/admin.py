from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Curate_Customer)
admin.site.register(Curate_Query)
admin.site.register(Article_Curate_Query)
admin.site.register(Curate_Customer_Selection)
admin.site.register(Curate_Rejection_Reasons)
admin.site.register(Curate_Query_Cluster)
admin.site.register(Curate_Recipient)
