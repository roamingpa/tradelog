from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView

from catalog.models import Card
from contacts.models import Contact
from transactions.forms import PurchaseForm, PurchaseItemFormSet, SaleForm, SaleItemFormSet
from transactions.models import Purchase, PurchaseItem, Sale, SaleItem
from transactions.whatsapp_parser import parse_whatsapp_import


class PurchaseListView(LoginRequiredMixin, ListView):
    model = Purchase
    template_name = 'transactions/purchase_list.html'
    context_object_name = 'purchases'
    paginate_by = 25

    def get_queryset(self):
        queryset = Purchase.objects.filter(owner=self.request.user).select_related('seller', 'location').prefetch_related('items__card')
        status = self.request.GET.get('status', '')
        method = self.request.GET.get('method', '')
        query = self.request.GET.get('q', '').strip()
        if status == 'pending':
            queryset = queryset.filter(is_completed=False)
        elif status == 'completed':
            queryset = queryset.filter(is_completed=True)
        if method == 'shipping':
            queryset = queryset.filter(is_shipping=True)
        elif method == 'pickup':
            queryset = queryset.filter(is_shipping=False)
        if query:
            queryset = queryset.filter(
                Q(seller__name__icontains=query)
                | Q(location__name__icontains=query)
                | Q(items__card__code__icontains=query)
                | Q(items__card__name__icontains=query)
            ).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filters'] = {
            'q': self.request.GET.get('q', '').strip(),
            'status': self.request.GET.get('status', ''),
            'method': self.request.GET.get('method', ''),
        }
        params = self.request.GET.copy()
        params.pop('page', None)
        context['filter_querystring'] = urlencode(params, doseq=True)
        return context


class SaleListView(LoginRequiredMixin, ListView):
    model = Sale
    template_name = 'transactions/sale_list.html'
    context_object_name = 'sales'
    paginate_by = 25

    def get_queryset(self):
        queryset = Sale.objects.filter(owner=self.request.user).select_related('buyer', 'location').prefetch_related('items__card')
        status = self.request.GET.get('status', '')
        method = self.request.GET.get('method', '')
        query = self.request.GET.get('q', '').strip()
        if status == 'pending':
            queryset = queryset.filter(is_completed=False)
        elif status == 'completed':
            queryset = queryset.filter(is_completed=True)
        if method == 'shipping':
            queryset = queryset.filter(is_shipping=True)
        elif method == 'pickup':
            queryset = queryset.filter(is_shipping=False)
        if query:
            queryset = queryset.filter(
                Q(buyer__name__icontains=query)
                | Q(location__name__icontains=query)
                | Q(items__card__code__icontains=query)
                | Q(items__card__name__icontains=query)
            ).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filters'] = {
            'q': self.request.GET.get('q', '').strip(),
            'status': self.request.GET.get('status', ''),
            'method': self.request.GET.get('method', ''),
        }
        params = self.request.GET.copy()
        params.pop('page', None)
        context['filter_querystring'] = urlencode(params, doseq=True)
        return context


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
def whatsapp_import_preview(request, transaction_kind):
    if transaction_kind not in {'purchase', 'sale'}:
        return JsonResponse({'ok': False, 'error': 'Tipo de transacción inválido.'}, status=400)

    full_name = request.user.get_full_name()
    result = parse_whatsapp_import(
        request.POST.get('text', ''),
        transaction_kind=transaction_kind,
        cards=Card.objects.all(),
        contacts=Contact.objects.filter(owner=request.user),
        own_names=[request.user.username, full_name],
    )
    return JsonResponse(result)


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
def purchase_items_mark_all_found(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk, owner=request.user)
    updated = PurchaseItem.objects.filter(purchase=purchase, is_found=False).update(is_found=True)
    return JsonResponse({'updated': updated})


@require_POST
@login_required
def sale_items_mark_all_found(request, pk):
    sale = get_object_or_404(Sale, pk=pk, owner=request.user)
    updated = SaleItem.objects.filter(sale=sale, is_found=False).update(is_found=True)
    return JsonResponse({'updated': updated})


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
