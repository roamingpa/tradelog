import json
from datetime import date, datetime

from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from tradelog.forms import StyledUserCreationForm
from transactions.models import Purchase, Sale


def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')


def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = StyledUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = StyledUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})


@login_required
def dashboard(request):
    date_str = request.GET.get('date', '')
    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date.today()
    except ValueError:
        selected_date = date.today()

    day_purchases = (
        Purchase.objects.filter(owner=request.user, fulfillment_date=selected_date)
        .select_related('seller', 'location')
        .prefetch_related('items__card')
    )
    day_sales = (
        Sale.objects.filter(owner=request.user, fulfillment_date=selected_date)
        .select_related('buyer', 'location')
        .prefetch_related('items__card')
    )

    map_points = []
    for p in day_purchases:
        if p.location:
            map_points.append({
                'kind': 'purchase',
                'id': p.pk,
                'label': f"Compra #{p.pk} — {p.seller or 'Sin vendedor'}",
                'location_name': p.location.name,
                'address': p.location.address,
                'time_from': p.time_from.strftime('%H:%M') if p.time_from else None,
                'time_to': p.time_to.strftime('%H:%M') if p.time_to else None,
                'completed': p.is_completed,
                'is_shipping': p.is_shipping,
                'url': f"/purchases/{p.pk}/",
            })
    for s in day_sales:
        if s.location:
            map_points.append({
                'kind': 'sale',
                'id': s.pk,
                'label': f"Venta #{s.pk} — {s.buyer or 'Sin comprador'}",
                'location_name': s.location.name,
                'address': s.location.address,
                'time_from': s.time_from.strftime('%H:%M') if s.time_from else None,
                'time_to': s.time_to.strftime('%H:%M') if s.time_to else None,
                'completed': s.is_completed,
                'is_shipping': s.is_shipping,
                'url': f"/sales/{s.pk}/",
            })

    context = {
        'recent_purchases': Purchase.objects.filter(owner=request.user).select_related('seller', 'location').prefetch_related('items')[:10],
        'recent_sales': Sale.objects.filter(owner=request.user).select_related('buyer', 'location').prefetch_related('items')[:10],
        'selected_date': selected_date,
        'day_purchases': day_purchases,
        'day_sales': day_sales,
        'map_points': json.dumps(map_points),
    }
    return render(request, 'dashboard.html', context)
