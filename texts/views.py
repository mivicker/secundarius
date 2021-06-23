import os
import json
import io
import csv
from django.contrib import messages
from django.shortcuts import render, redirect
from twilio.rest import Client
from .models import Words, Log
from .forms import UploadFileForm, UpdateWordsForm

#Load the twilio secrets file.
BASE_DIR = os.path.dirname(__file__)
key = os.path.join(BASE_DIR, "twilio_secrets.json")

with open(key) as f:
    secrets = json.load(f)

def home(request):
    context = {'words': Words.objects.first(),
        'form': UploadFileForm
    }
    return render(request, os.path.join('texts', 'home.html'), context)

def edit_words(request):
    context = {
        'form': UpdateWordsForm(initial={'words':Words.objects.first().words})
        }
    return render(request, os.path.join('texts', 'edit.html'), context)

def save(request):
    f = UpdateWordsForm(request.POST)
    new_words = f.save()
    return redirect('text-home')

def read_csv(file_input):
    data = file_input.read().decode('UTF-8')
    stream = io.StringIO(data)
    return csv.DictReader(stream)

def send_each(words, contacts, client):
    for contact in contacts:
        text = client.messages.create(
            body=words.words,
            from_='+13132514241',
            to=contact['Phone Number'])
        Log.objects.create(
            sender='13132514241',
            recipient=contact['Phone Number'][-4:],
            words=words,
            status='queued' #This is the typical Twilio api response.
        )

def send(request):
    words = Words.objects.first()    
    client = Client(secrets['TWILIO_ACCOUNT_SID'],
        secrets['TWILIO_AUTH_TOKEN'])
    texts = send_each(words, read_csv(request.FILES['file']), client)

    messages.success(request, f'Your messages were sent.')
    return redirect('text-home')