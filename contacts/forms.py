from django import forms

from .models import Contact

_C = {'class': 'form-control'}


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'whatsapp', 'instagram', 'email', 'other_references', 'notes']
        labels = {
            'name': 'Nombre',
            'whatsapp': 'WhatsApp',
            'instagram': 'Instagram',
            'email': 'Correo electrónico',
            'other_references': 'Otras referencias',
            'notes': 'Notas',
        }
        widgets = {
            'name': forms.TextInput(attrs={**_C, 'autofocus': True}),
            'whatsapp': forms.TextInput(attrs={**_C, 'placeholder': '+56912345678'}),
            'instagram': forms.TextInput(attrs={**_C, 'placeholder': '@usuario'}),
            'email': forms.EmailInput(attrs=_C),
            'other_references': forms.Textarea(attrs={**_C, 'rows': '2'}),
            'notes': forms.Textarea(attrs={**_C, 'rows': '2'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Default +569 only for new unbound forms
        if not args and not kwargs.get('data') and not kwargs.get('instance'):
            self.fields['whatsapp'].initial = '+569'
