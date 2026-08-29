from django.db import models
from django.urls import reverse

IMG_BASE = 'https://en.onepiece-cardgame.com/images/cardlist/card/'


class Card(models.Model):
    class Version(models.TextChoices):
        NORMAL = 'NORMAL', 'Normal'
        FOIL = 'FOIL', 'Foil'
        ALT_ART = 'ALT_ART', 'Arte Alternativo'
        SP = 'SP', 'Special / Secret Rare'
        PRE = 'PRE', 'Pre-release'

    code = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    version = models.CharField(max_length=10, choices=Version.choices, default=Version.NORMAL)
    image_suffix = models.CharField(max_length=10, blank=True, help_text="Ej: vacío=normal, _p1, _p2")
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['code', 'version']
        unique_together = [('code', 'version')]

    def save(self, *args, **kwargs):
        if self.code:
            self.code = self.code.upper().strip()
        super().save(*args, **kwargs)

    @property
    def image_url(self):
        if self.pk:
            return reverse('card-image', kwargs={'pk': self.pk})
        clean_code = self.code.upper().strip() if self.code else ''
        return f"{IMG_BASE}{clean_code}{self.image_suffix}.png"

    def __str__(self):
        return f"{self.code} — {self.name} ({self.get_version_display()})"
