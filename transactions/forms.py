from datetime import date

from django import forms
from django.forms import inlineformset_factory

from .models import Purchase, PurchaseItem, Sale, SaleItem

_C = {'class': 'form-control'}
_CL = {'class': 'form-control form-control-lg'}
_S = {'class': 'form-select ts-select'}


class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = [
            'date', 'fulfillment_date', 'is_shipping', 'seller', 'location',
            'time_from', 'time_to', 'instructions', 'currency', 'notes',
        ]
        labels = {
            'date': 'Fecha del acuerdo',
            'fulfillment_date': 'Fecha de retiro / envío',
            'is_shipping': 'Es por envío',
        }
        widgets = {
            'date': forms.DateInput(format='%Y-%m-%d', attrs={**_CL, 'type': 'date'}),
            'fulfillment_date': forms.DateInput(format='%Y-%m-%d', attrs={**_C, 'type': 'date'}),
            'is_shipping': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'seller': forms.Select(attrs=_S),
            'location': forms.Select(attrs=_S),
            'time_from': forms.TimeInput(attrs={**_C, 'type': 'time'}),
            'time_to': forms.TimeInput(attrs={**_C, 'type': 'time'}),
            'instructions': forms.Textarea(attrs={**_C, 'rows': '3'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={**_C, 'rows': '2'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk and 'date' not in self.initial:
            self.initial['date'] = date.today().strftime('%Y-%m-%d')
        if user is not None:
            self.fields['seller'].queryset = self.fields['seller'].queryset.filter(owner=user)
            self.fields['location'].queryset = self.fields['location'].queryset.filter(owner=user)


class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = [
            'date', 'fulfillment_date', 'is_shipping', 'buyer', 'location',
            'time_from', 'time_to', 'instructions', 'currency', 'notes',
        ]
        labels = {
            'date': 'Fecha del acuerdo',
            'fulfillment_date': 'Fecha de entrega / envío',
            'is_shipping': 'Es por envío',
        }
        widgets = {
            'date': forms.DateInput(format='%Y-%m-%d', attrs={**_CL, 'type': 'date'}),
            'fulfillment_date': forms.DateInput(format='%Y-%m-%d', attrs={**_C, 'type': 'date'}),
            'is_shipping': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'buyer': forms.Select(attrs=_S),
            'location': forms.Select(attrs=_S),
            'time_from': forms.TimeInput(attrs={**_C, 'type': 'time'}),
            'time_to': forms.TimeInput(attrs={**_C, 'type': 'time'}),
            'instructions': forms.Textarea(attrs={**_C, 'rows': '3'}),
            'currency': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={**_C, 'rows': '2'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk and 'date' not in self.initial:
            self.initial['date'] = date.today().strftime('%Y-%m-%d')
        if user is not None:
            self.fields['buyer'].queryset = self.fields['buyer'].queryset.filter(owner=user)
            self.fields['location'].queryset = self.fields['location'].queryset.filter(owner=user)


_ITEM_WIDGETS = {
    'card': forms.Select(attrs={'class': 'form-select ts-select'}),
    'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
    'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
}

PurchaseItemFormSet = inlineformset_factory(
    Purchase, PurchaseItem,
    fields=['card', 'quantity', 'unit_price'],
    extra=1,
    can_delete=True,
    widgets=_ITEM_WIDGETS,
)

SaleItemFormSet = inlineformset_factory(
    Sale, SaleItem,
    fields=['card', 'quantity', 'unit_price'],
    extra=1,
    can_delete=True,
    widgets=_ITEM_WIDGETS,
)
