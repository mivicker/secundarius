import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .handlers import build_frozen_context, build_fulfillment_context, build_route_context, load_csv
from .clean_up import clean_upload
from texts.forms import UploadFileForm

# Main landing page for site

@login_required
def landing(request):
    return render(request, "routes/landing.html", context={})

## Menu page for fulfillment system

@login_required
def fulfillment_menu(request):
    return render(request, 'routes/fulfillmenu.html')

### Download deliveries csv

@login_required
def download_menu(request):
    return render(request, 'routes/download_menu.html', context={})

@login_required
def deliveries_report(request):
    return render(request, 'routes/deliveries_report.html', context={})

@login_required
def download_deliveries(request):
    return render(request, 'routes/download_deliveries.html', context={})

@login_required
def delivery_csv(request):
    pass

### Prepare route documentation

@login_required
def csv_drop_off(request):
    return render(request, 'routes/csv_drop.html', context={'form':UploadFileForm})

@login_required
def post_csv(request):
    request.session['order'] = json.dumps(list(load_csv(request.FILES['file'])))
    return redirect('fulfillment-menu')

@login_required
def documents_menu(request):
    return render(request,'routes/documents-menu.html')

@login_required
def route_lists(request):
    file = request.session['order']
    cleaned = clean_upload(json.loads(file))
    order = build_route_context(cleaned)
    return render(request, 'routes/lists.html', context={'order': order})

@login_required
def fulfillment_tickets(request):
    file = request.session['order']
    cleaned = clean_upload(json.loads(file))
    order = build_fulfillment_context(cleaned)
    return render(request, 'routes/fulfillment.html', context={'order': order})

@login_required
def frozen_tickets(request):
    order = request.session['order']
    cleaned = clean_upload(json.loads(order))
    
    return render(request, 'routes/froz.html', context=build_frozen_context(cleaned))