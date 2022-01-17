import os
import time
from django.http import HttpResponse, HttpRequest
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.conf import settings
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
from .models import Broadcast, Reply
from .forms import UpdateReplyForm, UploadFileForm, UpdateBroadcastForm
from .logic import read_csv, send_each, filt_for_failures, SendDeps


@login_required
def home(request:HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        """
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            recipients = read_csv((request.FILES['file'].open()
                                                        .read()
                                                        .decode('UTF-8')))

            deps = SendDeps(
                words=Broadcast.objects.first().words,
                from_=settings.TWILIO_NUMBER,  
                client=Client(
                    settings.TWILIO_ACCOUNT_SID,
                    settings.TWILIO_AUTH_TOKEN),
                )

            responses = send_each(recipients)(deps)
            failures = list(filt_for_failures(responses))

            if not failures:
                messages.success(request, 'Your messages were sent.')
            else:
                for failure in failures:
                    messages.error(request, failure._inner_value)
            return redirect('text-home')
        messages.error(
            request, 
            "The csv you submitted doesn't have the necessary columns."
            )
        """
        time.sleep(4)
        return redirect('text-home')

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
    broadcast.save()
    return redirect('text-home')


@login_required
def save_reply(request):
    f = UpdateReplyForm(request.POST)
    f.save()
    return redirect('text-home')


@csrf_exempt
def receive(request):
    reply = Reply.objects.first()
    response = MessagingResponse()
    response.message(reply.words)
    return HttpResponse(str(response))
