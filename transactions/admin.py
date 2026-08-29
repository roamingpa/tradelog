from django.contrib import admin

from .models import Purchase, PurchaseItem, Sale, SaleItem


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('date', 'owner', 'fulfillment_date', 'is_shipping', 'seller', 'location', 'currency', 'total', 'is_completed')
    list_filter = ('owner', 'currency', 'date', 'is_shipping', 'is_completed')
    search_fields = ('seller__name', 'location__name')
    inlines = [PurchaseItemInline]


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('date', 'owner', 'fulfillment_date', 'is_shipping', 'buyer', 'location', 'currency', 'total', 'is_completed')
    list_filter = ('owner', 'currency', 'date', 'is_shipping', 'is_completed')
    search_fields = ('buyer__name', 'location__name')
    inlines = [SaleItemInline]
