import os
import json
from django.contrib import messages
from django.shortcuts import render, redirect
from twilio.rest import Client

def home(request):
    return render(request, os.path.join('texts', 'home.html'), {})

def send(request):
    with open('twilio_secrets.json') as f:
        secrets = json.load(f)
    account_sid = secrets['TWILIO_ACCOUNT_SID']
    auth_token = secrets['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)
    pass_hash = request.POST['password']
    if pass_hash == 'out of bananas':
        message = client.messages \
            .create(
                body = request.POST['text-message'],
                from_ = '+13132514241',
                to = '+17342775603'
            )

        messages.success(request, f'The status of your message was {message.status}.')
        return redirect('text-home')
    messages.error(request, 'This was the wrong password')
    return redirect('text-home')