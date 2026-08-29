from django.urls import path

from .views import card_image_proxy, card_new

urlpatterns = [
    path('cards/new/', card_new, name='card-new'),
    path('cards/<int:pk>/image/', card_image_proxy, name='card-image'),
]
