from django import forms

from .models import Card

_C = {'class': 'form-control'}


class CardForm(forms.ModelForm):
    class Meta:
        model = Card
        fields = ['code', 'name', 'version', 'image_suffix', 'notes']
        labels = {
            'code': 'Código',
            'name': 'Nombre',
            'version': 'Versión',
            'image_suffix': 'Sufijo de imagen',
            'notes': 'Notas',
        }
        widgets = {
            'code': forms.TextInput(attrs={**_C, 'autofocus': True, 'placeholder': 'OP01-001'}),
            'name': forms.TextInput(attrs=_C),
            'version': forms.Select(attrs={'class': 'form-select'}),
            'image_suffix': forms.TextInput(attrs={**_C, 'placeholder': 'vacío=normal, _p1, _p2…'}),
            'notes': forms.Textarea(attrs={**_C, 'rows': '2'}),
        }
