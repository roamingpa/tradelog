from django.contrib import admin

from .models import Contact


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'whatsapp', 'instagram', 'email')
    list_filter = ('owner',)
    search_fields = ('name', 'whatsapp', 'instagram', 'email')
