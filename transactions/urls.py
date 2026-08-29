from django.urls import path

from .views import (
    PurchaseDetailView, PurchaseListView,
    SaleDetailView, SaleListView,
    purchase_create, purchase_item_toggle_found, purchase_toggle_completed,
    sale_create, sale_item_toggle_found, sale_toggle_completed,
)

urlpatterns = [
    path('purchases/', PurchaseListView.as_view(), name='purchase-list'),
    path('purchases/new/', purchase_create, name='purchase-new'),
    path('purchases/<int:pk>/', PurchaseDetailView.as_view(), name='purchase-detail'),
    path('purchases/<int:pk>/edit/', purchase_create, name='purchase-edit'),
    path('purchases/<int:pk>/toggle/', purchase_toggle_completed, name='purchase-toggle'),
    path('purchases/items/<int:pk>/toggle-found/', purchase_item_toggle_found, name='purchase-item-toggle-found'),
    path('sales/', SaleListView.as_view(), name='sale-list'),
    path('sales/new/', sale_create, name='sale-new'),
    path('sales/<int:pk>/', SaleDetailView.as_view(), name='sale-detail'),
    path('sales/<int:pk>/edit/', sale_create, name='sale-edit'),
    path('sales/<int:pk>/toggle/', sale_toggle_completed, name='sale-toggle'),
    path('sales/items/<int:pk>/toggle-found/', sale_item_toggle_found, name='sale-item-toggle-found'),
]
