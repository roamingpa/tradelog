from django.urls import path

from .views import card_image_proxy, card_new, collection_view

urlpatterns = [
    path('collection/', collection_view, name='collection'),
    path('cards/new/', card_new, name='card-new'),
    path('cards/<int:pk>/image/', card_image_proxy, name='card-image'),
]
