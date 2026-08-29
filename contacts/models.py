from django.conf import settings
from django.db import models


class Contact(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contacts')
    name = models.CharField(max_length=200)
    whatsapp = models.CharField(max_length=30, blank=True)
    instagram = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    other_references = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
