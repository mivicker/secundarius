import io
import csv
from .models import Log, Reply


def read_csv(file_input):
    data = file_input.read().decode('UTF-8')
    stream = io.StringIO(data)
    return csv.DictReader(stream)

def send_each(words, contacts, client):
    reply = Reply.objects.first()

    for contact in contacts:
        text = client.messages.create(
            body=words.words,
            from_='+13132514241',
            to=contact['Phone Number'])
        Log.objects.create(
            sender='13132514241',
            recipient=contact['Phone Number'],
            words=words,
            reply=reply,
            status='queued' #This is the typical Twilio api response.
        )