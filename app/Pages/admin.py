from django.contrib import admin
from Pages.models import LinkList

class LinkListAdmin(admin.ModelAdmin):
    list_display = ('title',)
    ordering = ('title',)

admin.site.register(LinkList, LinkListAdmin)
