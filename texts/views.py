import os
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.conf import settings
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from .models import Broadcast, Reply, Log, Received, FillField
from .forms import UpdateReplyForm, UploadFileForm, UpdateBroadcastForm
from .handlers import read_csv, send_each, pluck_variables

@login_required
def home(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            recipients = read_csv(request.FILES['file'].open())
            words = Broadcast.objects.first()    
            client = Client(settings.TWILIO_ACCOUNT_SID,
               settings.TWILIO_AUTH_TOKEN)
            texts = send_each(words, recipients, client)

            messages.success(request, f'Your messages were sent.')
            return redirect('text-home')
        messages.error(request, f'The csv you submitted doesn\'t have the necessary columns.')

    context = {
        'words': Broadcast.objects.first(),
        'reply': Reply.objects.first(),
        'form': UploadFileForm()
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
    broadcast = UpdateBroadcastForm(request.POST)
    new_broadcast = broadcast.save()
    for variable in pluck_variables(new_broadcast.words):
        FillField.objects.create(
            field_name=variable, broadcast=new_broadcast)

    return redirect('text-home')

@login_required
def save_reply(request):
    f = UpdateReplyForm(request.POST)
    new_reply = f.save()
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