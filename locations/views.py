import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .forms import LocationForm


@login_required
@require_http_methods(['GET', 'POST'])
def location_new(request):
    select_id = request.GET.get('select', request.POST.get('select_id', ''))
    if request.method == 'POST':
        form = LocationForm(request.POST)
        if form.is_valid():
            location = form.save(commit=False)
            location.owner = request.user
            location.save()
            response = HttpResponse()
            response['HX-Trigger'] = json.dumps(
                {'entityCreated': {'id': str(location.id), 'name': str(location), 'selectId': select_id}}
            )
            return response
        return render(request, 'locations/_form_partial.html', {'form': form, 'select_id': select_id})
    return render(request, 'locations/_form_partial.html', {'form': LocationForm(), 'select_id': select_id})
