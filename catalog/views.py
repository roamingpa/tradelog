import json
import urllib.request
from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

from django.db.models import Q, Sum

from .forms import CardForm
from .models import Card, IMG_BASE


@login_required
def collection_view(request):
    from transactions.models import PurchaseItem
    search_query = request.GET.get('q', '').strip()
    version_filter = request.GET.get('version', '').strip()

    items = (
        PurchaseItem.objects.filter(purchase__owner=request.user)
        .values('card__id', 'card__code', 'card__name', 'card__version', 'card__image_suffix')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('card__code', 'card__version')
    )

    if search_query:
        items = items.filter(
            Q(card__code__icontains=search_query) | Q(card__name__icontains=search_query)
        )
    if version_filter:
        items = items.filter(card__version=version_filter)

    version_dict = dict(Card.Version.choices)
    cards_data = []
    for item in items:
        cards_data.append({
            'id': item['card__id'],
            'code': item['card__code'],
            'name': item['card__name'],
            'version': item['card__version'],
            'version_display': version_dict.get(item['card__version'], item['card__version']),
            'total_quantity': item['total_quantity'],
            'image_url': f"/catalog/cards/{item['card__id']}/image/",
        })

    total_cards_count = sum(i['total_quantity'] for i in cards_data)
    unique_cards_count = len(cards_data)

    context = {
        'cards_data': cards_data,
        'search_query': search_query,
        'version_filter': version_filter,
        'versions': Card.Version.choices,
        'total_cards_count': total_cards_count,
        'unique_cards_count': unique_cards_count,
    }
    return render(request, 'catalog/collection.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def card_new(request):
    select_id = request.GET.get('select', request.POST.get('select_id', ''))
    if request.method == 'POST':
        form = CardForm(request.POST)
        if form.is_valid():
            card = form.save()
            response = HttpResponse()
            response['HX-Trigger'] = json.dumps(
                {'entityCreated': {'id': str(card.id), 'name': str(card), 'selectId': select_id}}
            )
            return response
        return render(request, 'catalog/_form_partial.html', {'form': form, 'select_id': select_id})
    return render(request, 'catalog/_form_partial.html', {'form': CardForm(), 'select_id': select_id})


@login_required
def card_image_proxy(request, pk):
    card = get_object_or_404(Card, pk=pk)
    clean_code = card.code.upper().strip()
    filename = f"{clean_code}{card.image_suffix}.png"
    
    cache_dir = Path(settings.BASE_DIR) / 'media' / 'card_cache'
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / filename

    if cache_path.exists():
        with open(cache_path, 'rb') as f:
            content = f.read()
        return HttpResponse(content, content_type='image/png')

    remote_url = f"{IMG_BASE}{filename}"
    try:
        req = urllib.request.Request(remote_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content = resp.read()
        with open(cache_path, 'wb') as f:
            f.write(content)
        return HttpResponse(content, content_type='image/png')
    except Exception as exc:
        raise Http404(f"Could not load card image: {exc}")
