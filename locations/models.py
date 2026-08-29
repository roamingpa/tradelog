from django.conf import settings
from django.db import models


class Location(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='locations')
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=500, blank=True)
    instructions = models.TextField(blank=True)
    maps_link = models.URLField(max_length=1000, blank=True, help_text="URL de Google Maps (link o embed)")
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
