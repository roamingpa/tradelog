from django import forms

from .models import Location

_C = {'class': 'form-control'}


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'address', 'instructions', 'maps_link']
        widgets = {
            'name': forms.TextInput(attrs={**_C, 'autofocus': True}),
            'address': forms.TextInput(attrs=_C),
            'instructions': forms.Textarea(attrs={**_C, 'rows': '3'}),
            'maps_link': forms.HiddenInput(),
        }
