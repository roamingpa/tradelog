from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView

from catalog.models import Card
from contacts.models import Contact
from transactions.forms import PurchaseForm, PurchaseItemFormSet, SaleForm, SaleItemFormSet
from transactions.models import Purchase, PurchaseItem, Sale, SaleItem


class PurchaseListView(LoginRequiredMixin, ListView):
    model = Purchase
    template_name = 'transactions/purchase_list.html'
    context_object_name = 'purchases'
    paginate_by = 25

    def get_queryset(self):
        return Purchase.objects.filter(owner=self.request.user).select_related('seller', 'location').prefetch_related('items')


class SaleListView(LoginRequiredMixin, ListView):
    model = Sale
    template_name = 'transactions/sale_list.html'
    context_object_name = 'sales'
    paginate_by = 25

    def get_queryset(self):
        return Sale.objects.filter(owner=self.request.user).select_related('buyer', 'location').prefetch_related('items')


class PurchaseDetailView(LoginRequiredMixin, DetailView):
    model = Purchase
    template_name = 'transactions/purchase_detail.html'
    context_object_name = 'purchase'

    def get_queryset(self):
        return Purchase.objects.filter(owner=self.request.user).select_related('seller', 'location').prefetch_related('items__card')


class SaleDetailView(LoginRequiredMixin, DetailView):
    model = Sale
    template_name = 'transactions/sale_detail.html'
    context_object_name = 'sale'

    def get_queryset(self):
        return Sale.objects.filter(owner=self.request.user).select_related('buyer', 'location').prefetch_related('items__card')


@login_required
def purchase_create(request, pk=None):
    cards = Card.objects.all()
    contacts = Contact.objects.filter(owner=request.user)
    instance = get_object_or_404(Purchase, pk=pk, owner=request.user) if pk else None
    if request.method == 'POST':
        form = PurchaseForm(request.POST, instance=instance, user=request.user)
        formset = PurchaseItemFormSet(request.POST, prefix='items', instance=instance)
        if form.is_valid() and formset.is_valid():
            purchase = form.save(commit=False)
            purchase.owner = request.user
            purchase.save()
            formset.instance = purchase
            formset.save()
            messages.success(request, 'Compra actualizada.' if instance else 'Compra registrada.')
            return redirect('purchase-detail', pk=purchase.pk)
    else:
        form = PurchaseForm(instance=instance, user=request.user)
        formset = PurchaseItemFormSet(prefix='items', instance=instance)
    return render(request, 'transactions/purchase_form.html', {
        'form': form, 'formset': formset, 'cards': cards, 'contacts': contacts, 'editing': instance is not None,
    })


@login_required
def sale_create(request, pk=None):
    cards = Card.objects.all()
    contacts = Contact.objects.filter(owner=request.user)
    instance = get_object_or_404(Sale, pk=pk, owner=request.user) if pk else None

    if request.method == 'POST':
        form = SaleForm(request.POST, instance=instance, user=request.user)
        formset = SaleItemFormSet(request.POST, prefix='items', instance=instance)
        if form.is_valid() and formset.is_valid():
            sale = form.save(commit=False)
            sale.owner = request.user
            sale.save()
            formset.instance = sale
            formset.save()
            messages.success(request, 'Venta actualizada.' if instance else 'Venta registrada.')
            return redirect('sale-detail', pk=sale.pk)
    else:
        form = SaleForm(instance=instance, user=request.user)
        formset = SaleItemFormSet(prefix='items', instance=instance)
    return render(request, 'transactions/sale_form.html', {
        'form': form, 'formset': formset, 'cards': cards, 'contacts': contacts, 'editing': instance is not None,
    })


@require_POST
@login_required
def purchase_toggle_completed(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk, owner=request.user)
    purchase.is_completed = not purchase.is_completed
    purchase.save(update_fields=['is_completed'])
    return JsonResponse({'is_completed': purchase.is_completed})


@require_POST
@login_required
def sale_toggle_completed(request, pk):
    sale = get_object_or_404(Sale, pk=pk, owner=request.user)
    sale.is_completed = not sale.is_completed
    sale.save(update_fields=['is_completed'])
    return JsonResponse({'is_completed': sale.is_completed})


@require_POST
@login_required
def purchase_item_toggle_found(request, pk):
    item = get_object_or_404(PurchaseItem, pk=pk, purchase__owner=request.user)
    item.is_found = not item.is_found
    item.save(update_fields=['is_found'])
    return JsonResponse({'is_found': item.is_found})


@require_POST
@login_required
def sale_item_toggle_found(request, pk):
    item = get_object_or_404(SaleItem, pk=pk, sale__owner=request.user)
    item.is_found = not item.is_found
    item.save(update_fields=['is_found'])
    return JsonResponse({'is_found': item.is_found})
