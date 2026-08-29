import urllib.parse

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

    @property
    def is_address_url(self):
        return bool(self.address and (self.address.startswith('http://') or self.address.startswith('https://')))

    @property
    def google_maps_direct_url(self):
        # 1. If maps_link is a direct google maps link (not embed iframe), use it
        if self.maps_link and ('google.com/maps' in self.maps_link or 'maps.app.goo.gl' in self.maps_link):
            if 'output=embed' not in self.maps_link:
                return self.maps_link
        # 2. If address itself is a URL, use it directly
        if self.is_address_url:
            return self.address
        # 3. If exact coordinates are available
        if self.latitude and self.longitude:
            return f"https://www.google.com/maps/search/?api=1&query={self.latitude},{self.longitude}"
        # 4. Fallback search by address text or name
        query = self.address or self.name
        if query:
            return f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(query)}"
        return ""

    def __str__(self):
        return self.name
