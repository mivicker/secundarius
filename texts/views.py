import os
import json
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from twilio.rest import Client
from .models import Words, Log
from .forms import UploadFileForm, UpdateWordsForm
from .handlers import read_csv, send_each

#Load the twilio secrets file.
BASE_DIR = os.path.dirname(__file__)
key = os.path.join(BASE_DIR, "twilio_secrets.json")

with open(key) as f:
    secrets = json.load(f)

@login_required
def home(request):
    context = {'words': Words.objects.first(),
        'form': UploadFileForm
    }
    return render(request, os.path.join('texts', 'home.html'), context)

@login_required
def edit_words(request):
    context = {
        'form': UpdateWordsForm(initial={'words':Words.objects.first().words})
        }
    return render(request, os.path.join('texts', 'edit.html'), context)

@login_required
def save(request):
    f = UpdateWordsForm(request.POST)
    new_words = f.save()
    return redirect('text-home')

@login_required
def send(request):
    words = Words.objects.first()    
    client = Client(secrets['TWILIO_ACCOUNT_SID'],
        secrets['TWILIO_AUTH_TOKEN'])
    texts = send_each(words, read_csv(request.FILES['file']), client)

    messages.success(request, f'Your messages were sent.')
    return redirect('text-home')

@login_required
def text_logs(request):
    context = {'logs':Log.objects.all()}
    return render(
        request, os.path.join('texts', 'logs.html'), context)