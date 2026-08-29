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

    # Build unified agenda items list with rich sorting metadata
    agenda_items = []
    for p in day_purchases:
        agenda_items.append({
            'kind': 'purchase',
            'pk': p.pk,
            'party': p.seller.name if p.seller else 'Sin vendedor',
            'location': p.location,
            'time_from': p.time_from,
            'time_to': p.time_to,
            'time_str': p.time_from.strftime('%H:%M') if p.time_from else '99:99',
            'is_completed': p.is_completed,
            'is_shipping': p.is_shipping,
            'items_count': sum(i.quantity for i in p.items.all()),
            'total': p.formatted_total(),
            'currency': p.currency,
            'detail_url': f"/purchases/{p.pk}/",
            'toggle_url': f"/purchases/{p.pk}/toggle/",
        })

    for s in day_sales:
        agenda_items.append({
            'kind': 'sale',
            'pk': s.pk,
            'party': s.buyer.name if s.buyer else 'Sin comprador',
            'location': s.location,
            'time_from': s.time_from,
            'time_to': s.time_to,
            'time_str': s.time_from.strftime('%H:%M') if s.time_from else '99:99',
            'is_completed': s.is_completed,
            'is_shipping': s.is_shipping,
            'items_count': sum(i.quantity for i in s.items.all()),
            'total': s.formatted_total(),
            'currency': s.currency,
            'detail_url': f"/sales/{s.pk}/",
            'toggle_url': f"/sales/{s.pk}/toggle/",
        })

    # Default sort: by time_from ascending (empty time goes to bottom)
    agenda_items.sort(key=lambda x: (x['time_str'], x['party'].lower()))

    map_points = []
    for item in agenda_items:
        if item['location']:
            loc = item['location']
            map_points.append({
                'kind': item['kind'],
                'id': item['pk'],
                'label': f"{'Compra' if item['kind'] == 'purchase' else 'Venta'} #{item['pk']} — {item['party']}",
                'location_name': loc.name,
                'address': loc.address,
                'lat': loc.latitude,
                'lon': loc.longitude,
                'time_from': item['time_from'].strftime('%H:%M') if item['time_from'] else None,
                'time_to': item['time_to'].strftime('%H:%M') if item['time_to'] else None,
                'completed': item['is_completed'],
                'is_shipping': item['is_shipping'],
                'url': item['detail_url'],
            })

    context = {
        'recent_purchases': Purchase.objects.filter(owner=request.user).select_related('seller', 'location').prefetch_related('items')[:10],
        'recent_sales': Sale.objects.filter(owner=request.user).select_related('buyer', 'location').prefetch_related('items')[:10],
        'selected_date': selected_date,
        'agenda_items': agenda_items,
        'day_purchases': day_purchases,
        'day_sales': day_sales,
        'map_points': json.dumps(map_points),
    }
    return render(request, 'dashboard.html', context)
