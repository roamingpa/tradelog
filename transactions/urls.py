from django.urls import path

from .views import (
    PurchaseDetailView, PurchaseListView,
    SaleDetailView, SaleListView,
    purchase_create, purchase_item_toggle_found, purchase_items_mark_all_found, purchase_toggle_completed,
    sale_create, sale_item_toggle_found, sale_toggle_completed, whatsapp_import_preview,
    sale_items_mark_all_found,
)

urlpatterns = [
    path('imports/whatsapp/<str:transaction_kind>/preview/', whatsapp_import_preview, name='whatsapp-import-preview'),
    path('purchases/', PurchaseListView.as_view(), name='purchase-list'),
    path('purchases/new/', purchase_create, name='purchase-new'),
    path('purchases/<int:pk>/', PurchaseDetailView.as_view(), name='purchase-detail'),
    path('purchases/<int:pk>/edit/', purchase_create, name='purchase-edit'),
    path('purchases/<int:pk>/toggle/', purchase_toggle_completed, name='purchase-toggle'),
    path('purchases/<int:pk>/items/mark-all-found/', purchase_items_mark_all_found, name='purchase-items-mark-all-found'),
    path('purchases/items/<int:pk>/toggle-found/', purchase_item_toggle_found, name='purchase-item-toggle-found'),
    path('sales/', SaleListView.as_view(), name='sale-list'),
    path('sales/new/', sale_create, name='sale-new'),
    path('sales/<int:pk>/', SaleDetailView.as_view(), name='sale-detail'),
    path('sales/<int:pk>/edit/', sale_create, name='sale-edit'),
    path('sales/<int:pk>/toggle/', sale_toggle_completed, name='sale-toggle'),
    path('sales/<int:pk>/items/mark-all-found/', sale_items_mark_all_found, name='sale-items-mark-all-found'),
    path('sales/items/<int:pk>/toggle-found/', sale_item_toggle_found, name='sale-item-toggle-found'),
]
