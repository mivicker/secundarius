import os
from django.shortcuts import render

def froz_view(request):
    return render(request, os.path.join('counts', 'froz.html'))