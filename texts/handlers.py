import io
import csv
from django.conf import settings
from .models import Log, Reply


def read_csv(file_input):
    data = file_input.read().decode('UTF-8')
    stream = io.StringIO(data)
    return csv.DictReader(stream)

def send_each(words, contacts, client):
    phone_number = settings.TWILIO_NUMBER
    reply = Reply.objects.first()

    for contact in contacts:
        text = client.messages.create(
            body=words.words,
            from_=f'+{phone_number}',
            to=contact['Phone Number'])
        Log.objects.create(
            sender=phone_number,
            recipient=contact['Phone Number'],
            words=words,
            reply=reply,
            status='queued' #This is the typical Twilio api response.
        )

def lookup_reply(recipient):
    return Log.objects.filter(recipient=recipient).first().reply
