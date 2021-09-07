import json

from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .business.handlers import (build_frozen_context, build_fulfillment_context, 
                       build_route_context, load_csv)
from .business.clean_up import clean_upload
from .forms import DateForm
from .business.download_deliveries import collect_time_blocks, make_csv

from texts.forms import UploadFileForm

# Main landing page for site

@login_required
def landing(request):
    return render(request, "routes/landing.html", context={})

# Menu page for fulfillment system

@login_required
def fulfillment_menu(request):
    return render(request, 'routes/fulfillmenu.html')

# Download deliveries csv

@login_required
def select_date(request):
    if request.method == "POST":
        form = DateForm(request.POST)
        if form.is_valid():
            date = form.cleaned_data['date']
            time_blocks = collect_time_blocks(date)
            request.session['delivery date'] = date.strftime('%m-%d-%Y')
            request.session['time blocks'] = time_blocks
        return redirect('select-time')
    return render(request, 'routes/select_date.html', context={'form':DateForm()})

@login_required
def select_time(request):
    return render(request, 'routes/select_time.html', context={
        'available_blocks' : reversed(request.session['time blocks'].keys())
    })

@login_required
def download_csv(request, time):
    blocks = request.session['time blocks']
    date = request.session['delivery date']
    csv = make_csv(blocks[time])

    response = HttpResponse(csv)

    response['Content-Type'] = 'application/vnd.ms-excel'
    response['Content-Disposition'] = f'attachment; filename="Deliveries{date}{time}.csv"'

    return response

# Prepare route documentation

@login_required
def csv_drop_off(request):
    return render(request, 'routes/csv_drop.html', context={'form':UploadFileForm})

@login_required
def post_csv(request):
    request.session['order'] = json.dumps(list(load_csv(request.FILES['file'])))
    return redirect('doc-menu')

@login_required
def documents_menu(request):
    return render(request,'routes/documents-menu.html')

@login_required
def route_lists(request):
    try:
        file = request.session['order']
        cleaned = clean_upload(json.loads(file))
        order = build_route_context(cleaned)
        return render(request, 'routes/lists.html', context={'order': order})
    except KeyError:
        return redirect('upload-error')

@login_required
def fulfillment_tickets(request):
    file = request.session['order']
    try:
        cleaned = clean_upload(json.loads(file))
        order = build_fulfillment_context(cleaned)
        return render(request, 'routes/fulfillment.html', context={'order': order})
    except KeyError:
        return redirect('upload-error')

@login_required
def upload_error(request):
    return render(request, 'routes/upload_error.html')

@login_required
def frozen_tickets(request):
    try:
        order = request.session['order']
        cleaned = clean_upload(json.loads(order))
        return render(request, 'routes/froz.html', context=build_frozen_context(cleaned))
    except KeyError:
        return redirect('upload-error')