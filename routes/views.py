import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .handlers import build_fulfillment_context, build_route_context, load_csv
from texts.forms import UploadFileForm

@login_required
def csv_drop_off(request):
    return render(request, 'routes/csv_drop.html', context={'form':UploadFileForm})

@login_required
def post_csv(request):
    request.session['order'] = json.dumps(list(load_csv(request.FILES['file'])))
    return redirect('fulfillment-menu')

@login_required
def documents_menu(request):
    return render('routes/menu.html')

@login_required
def fulfillment_tickets(request):
    file = request.session['order']
    order = build_fulfillment_context(json.loads(file))
    return render(request, 'routes/fulfillment.html', context={'order': order})

@login_required
def route_lists(request):
    file = request.session['order']
    order = build_route_context(json.loads(file))
    return render(request, 'routes/lists.html', context={'order': order})

@login_required
def landing(request):
    return render(request, "routes/landing.html", context={})

@login_required
def fulfillment_menu(request):
    return render(request, "routes/menu.html", context={})
"""
def frozen_tickets(request):
    csv = request.FILES['file']
    order = build_frozen_context(csv)
    return render(request, 'routes/froz.html', context={'order': order})
"""