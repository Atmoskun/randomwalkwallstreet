# tracking/admin.py
from django.contrib import admin
from .models import PageView, SiteVisit

@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('path', 'visits')
    search_fields = ('path',)

@admin.register(SiteVisit)
class SiteVisitAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'path', 'session_key')
    list_filter = ('timestamp', 'path')
    
# Register your models here.
