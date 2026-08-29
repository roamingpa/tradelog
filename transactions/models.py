from django.conf import settings
from django.db import models

from catalog.models import Card
from contacts.models import Contact
from locations.models import Location


class Currency(models.TextChoices):
    CLP = 'CLP', 'CLP (Peso Chileno)'
    USD = 'USD', 'USD (Dólar)'
    ARS = 'ARS', 'ARS (Peso Argentino)'


def format_currency_amount(amount, currency):
    if currency == Currency.CLP:
        return f"{int(amount):,}".replace(',', '.')
    return f"{amount:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')


class Purchase(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='purchases')
    date = models.DateField(help_text='Fecha en que se concretó la compra')
    fulfillment_date = models.DateField(
        null=True, blank=True, help_text='Fecha en que debo retirar o recibir por envío'
    )
    is_shipping = models.BooleanField(default=False, help_text='Marca si es por envío en vez de retiro presencial')
    seller = models.ForeignKey(
        Contact, null=True, blank=True, on_delete=models.SET_NULL, related_name='purchases_as_seller'
    )
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL)
    time_from = models.TimeField(null=True, blank=True)
    time_to = models.TimeField(null=True, blank=True)
    instructions = models.TextField(blank=True)
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.CLP)
    notes = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False, help_text='Marca si la compra ya fue retirada')

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Compra {self.date} — {self.seller or 'Sin vendedor'}"

    def total(self):
        return sum(item.subtotal() for item in self.items.all())

    def formatted_total(self):
        return format_currency_amount(self.total(), self.currency)


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items')
    card = models.ForeignKey(Card, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    def subtotal(self):
        return self.quantity * self.unit_price

    def formatted_unit_price(self):
        return format_currency_amount(self.unit_price, self.purchase.currency)

    def formatted_subtotal(self):
        return format_currency_amount(self.subtotal(), self.purchase.currency)

    def __str__(self):
        return f"{self.quantity}x {self.card}"


class Sale(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sales')
    date = models.DateField(help_text='Fecha en que se concretó la venta')
    fulfillment_date = models.DateField(
        null=True, blank=True, help_text='Fecha en que debo entregar o enviar'
    )
    is_shipping = models.BooleanField(default=False, help_text='Marca si es por envío en vez de entrega presencial')
    buyer = models.ForeignKey(
        Contact, null=True, blank=True, on_delete=models.SET_NULL, related_name='sales_as_buyer'
    )
    location = models.ForeignKey(Location, null=True, blank=True, on_delete=models.SET_NULL)
    time_from = models.TimeField(null=True, blank=True)
    time_to = models.TimeField(null=True, blank=True)
    instructions = models.TextField(blank=True)
    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.CLP)
    notes = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False, help_text='Marca si la venta ya fue entregada')

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Venta {self.date} — {self.buyer or 'Sin comprador'}"

    def total(self):
        return sum(item.subtotal() for item in self.items.all())

    def formatted_total(self):
        return format_currency_amount(self.total(), self.currency)


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    card = models.ForeignKey(Card, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    def subtotal(self):
        return self.quantity * self.unit_price

    def formatted_unit_price(self):
        return format_currency_amount(self.unit_price, self.sale.currency)

    def formatted_subtotal(self):
        return format_currency_amount(self.subtotal(), self.sale.currency)

    def __str__(self):
        return f"{self.quantity}x {self.card}"
