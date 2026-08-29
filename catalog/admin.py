from django.contrib import admin
from django.utils.html import format_html

from .models import Card


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'version', 'image_preview')
    list_filter = ('version',)
    search_fields = ('code', 'name')
    readonly_fields = ('image_preview',)

    @admin.display(description='Imagen')
    def image_preview(self, obj):
        return format_html(
            '<img src="{}" style="height:80px;border-radius:4px;" onerror="this.style.display=\'none\'">',
            obj.image_url,
        )
