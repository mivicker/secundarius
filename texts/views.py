import os
import json
from django.contrib import messages
from django.shortcuts import render, redirect
from twilio.rest import Client
from .models import Words
from .csv_loader import reader_from
from .forms import UploadFileForm, UpdateWordsForm

#Load the twilio secrets file.
BASE_DIR = os.path.dirname(__file__)
key = os.path.join(BASE_DIR, "twilio_secrets.json")

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

def send(request):
    with open(key) as f:
        secrets = json.load(f)
    account_sid = secrets['TWILIO_ACCOUNT_SID']
    auth_token = secrets['TWILIO_AUTH_TOKEN']
    
    client = Client(account_sid, auth_token)

    file = request.FILES['file']
    data = file.read().decode('UTF-8')

    pass_hash = request.POST['password']
    if pass_hash == 'out of bananas':
        texts = [client.messages \
            .create(
                body = Words.objects.first().words,
                from_ = '+13132514241',
                to = contact['Phone Number'] 
            ) for contact in reader_from(data)]

        messages.success(request, f'Your messages were sent.')
        return redirect('text-home')
    messages.error(request, 'This was the wrong password')
    return redirect('text-home')