from django.urls import path

from .views import location_new

urlpatterns = [
    path('new/', location_new, name='location-new'),
]
