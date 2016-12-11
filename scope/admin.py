from django.contrib import admin

# Register your models here.
from .models import Customer, Article, Source, AgentImap, UserProfile, Agent

admin.site.register(Customer)
admin.site.register(Article)
admin.site.register(Source)
admin.site.register(AgentImap)
admin.site.register(Agent)
admin.site.register(UserProfile)
