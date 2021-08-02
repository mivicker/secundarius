import json
from django.shortcuts import render, redirect
from .handlers import build_fulfillment_context, load_csv
from texts.forms import UploadFileForm

def csv_drop_off(request):
    return render(request, 'routes/csv_drop.html', context={'form':UploadFileForm})

def post_csv(request):
    request.session['order'] = json.dumps(list(load_csv(request.FILES['file'])))
    return redirect('pack-tickets')

def documents_menu(request):
    return render('routes/menu.html')

def fulfillment_tickets(request):
    file = request.session['order']
    order_dictionary = file
    order = build_fulfillment_context(json.loads(order_dictionary))
    return render(request, 'routes/simpleprint.html', context={'order': order})

"""
def route_lists(request):
    csv = request.FILES['file']
    order = build_route_context(csv)
    return render(request, 'routes/lists.html', context={'order': order})

def frozen_tickets(request):
    csv = request.FILES['file']
    order = build_frozen_context(csv)
    return render(request, 'routes/froz.html', context={'order': order})
"""