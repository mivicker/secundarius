import os
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.conf import settings
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from .models import Broadcast, Words, Log, Received
from .forms import UploadFileForm, UpdateBroadcastForm
from .handlers import read_csv, send_each

@login_required
def home(request):
    if Broadcast.objects.first():
        words = Broadcast.objects.first()
    else:
        words = Broadcast.objects.create(words="Please update this default message.")

    context = {'words': words,
        'form': UploadFileForm
    }
    return render(request, os.path.join('texts', 'home.html'), context)

@login_required
def edit_words(request):
    context = {
        'form': UpdateBroadcastForm(initial={'words':Broadcast.objects.first().words})
        }
    return render(request, os.path.join('texts', 'edit.html'), context)

@login_required
def save(request):
    f = UpdateBroadcastForm(request.POST)
    new_words = f.save()
    return redirect('text-home')

@login_required
def send(request):
    words = Broadcast.objects.first()    
    client = Client(settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN)
    texts = send_each(words, read_csv(request.FILES['file']), client)

    messages.success(request, f'Your messages were sent.')
    return redirect('text-home')

@login_required
def text_logs(request):
    context = {'logs':Log.objects.all()}
    return render(
        request, os.path.join('texts', 'logs.html'), context)

@csrf_exempt
def receive(request):
    content = request.POST['Body']
    from_= request.POST['From']
    r = Received.objects.create(content=content, from_num=from_)

    response = MessagingResponse()

    response.message("""
    PLEASE, DO NOT REPLY TO THIS MESSAGE
    To get in touch with Gleaners Healthcare Customer Service, please call (313) 725-4878.
    Reply STOP to opt-out of these messages.
    """)

    return HttpResponse(str(response))