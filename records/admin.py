from django.contrib import admin

from records.models import Content

class ContentAdmin(admin.ModelAdmin):
    list_display = ['id', 'text', 'is_active']

admin.site.register(Content, ContentAdmin)