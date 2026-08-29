from django import forms

from .models import Location

_C = {'class': 'form-control'}


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'address', 'instructions', 'maps_link', 'latitude', 'longitude']
        widgets = {
            'name': forms.TextInput(attrs={**_C, 'autofocus': True}),
            'address': forms.TextInput(attrs={**_C, 'placeholder': 'Ej: Av. Providencia 2198, Providencia'}),
            'instructions': forms.Textarea(attrs={**_C, 'rows': '3', 'placeholder': 'Ej: En la salida del metro línea 1, al lado del tótem'}),
            'maps_link': forms.HiddenInput(),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }
