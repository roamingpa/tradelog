from django.contrib import admin

from .models import Location


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'address', 'maps_link')
    list_filter = ('owner',)
    search_fields = ('name', 'address')
