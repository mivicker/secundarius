import json
from django.contrib import messages
from django.shortcuts import render, redirect
from twilio.rest import Client

def home(request):
    return render(request, 'texts/home.html', {})

def send(request):
    with open('twilio_secrets.json') as f:
        secrets = json.load(f)
    account_sid = secrets['TWILIO_ACCOUNT_SID']
    auth_token = secrets['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)

    message = client.messages \
        .create(
            body = "What up mike?",
            from_ = '+13132514241',
            to = '+17342775603'
        )

    messages.success(request, 'Your text has been sent.')
    return redirect('text-home')