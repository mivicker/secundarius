import os
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.conf import settings
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from .models import Broadcast, Reply, Log, Received
from .forms import UpdateReplyForm, UploadFileForm, UpdateBroadcastForm
from .handlers import read_csv, send_each

@login_required
def home(request):
    if Broadcast.objects.first():
        words = Broadcast.objects.first()
    else:
        words = Broadcast.objects.create(words="Please update this default message.")
    if Reply.objects.first():
        reply = Reply.objects.first()
    else:
        reply = Reply.objects.create(words="""DO NOT REPLY TO THIS MESSAGE 
            To talk to Gleaners Healthcare Customer Service, please call (313) 725-4878. 
            Reply STOP to opt out of text messages""")

    context = {'words': words,
        'reply': reply,
        'form': UploadFileForm
    }
    return render(request, os.path.join('texts', 'home.html'), context)

@login_required
def edit_broadcast(request):
    context = {
        'form': UpdateBroadcastForm(initial={'words':Broadcast.objects.first().words})
    }
    return render(request, os.path.join('texts', 'edit.html'), context)

@login_required
def edit_reply(request):
    context = {
        'form': UpdateReplyForm(initial={'words':Reply.objects.first().words})
    }
    return render(request, os.path.join('texts', 'edit-reply.html'), context)

@login_required
def save(request):
    f = UpdateBroadcastForm(request.POST)
    new_words = f.save()
    return redirect('text-home')

@login_required
def save_reply(request):
    f = UpdateReplyForm(request.POST)
    new_reply = f.save()
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
    
    reply = Reply.objects.first()

    response = MessagingResponse()

    response.message(reply.words)

    return HttpResponse(str(response))