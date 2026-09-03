import json

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .forms import ContactForm


@login_required
@require_http_methods(['GET', 'POST'])
def contact_new(request):
    select_id = request.GET.get('select', request.POST.get('select_id', ''))
    initial = {'name': request.GET.get('name', '').strip()}
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.owner = request.user
            contact.save()
            response = HttpResponse()
            response['HX-Trigger'] = json.dumps(
                {'entityCreated': {'id': str(contact.id), 'name': str(contact), 'selectId': select_id}}
            )
            return response
        return render(request, 'contacts/_form_partial.html', {'form': form, 'select_id': select_id})
    return render(request, 'contacts/_form_partial.html', {'form': ContactForm(initial=initial), 'select_id': select_id})
