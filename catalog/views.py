import json
import urllib.request
from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

from .forms import CardForm
from .models import Card, IMG_BASE


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
