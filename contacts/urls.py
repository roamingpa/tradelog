from django.urls import path

from .views import contact_new

urlpatterns = [
    path('new/', contact_new, name='contact-new'),
]
