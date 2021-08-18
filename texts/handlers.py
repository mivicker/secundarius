import io
import csv
from django.conf import settings
from .models import Log, Reply
from jinja2 import Environment, BaseLoader, meta

def read_csv(file_input):
    data = file_input.read().decode('UTF-8')
    stream = io.StringIO(data)
    return list(csv.DictReader(stream))

def send_each(words, contacts, client):
    phone_number = settings.TWILIO_NUMBER
    reply = Reply.objects.first()
    for contact in contacts:
        rendered = render_sms_template(words.words, contact)
        text = client.messages.create(
            body=rendered,
            from_=f'+{phone_number}',
            to=contact['phone'])
        Log.objects.create(
            sender=phone_number,
            recipient=contact['phone'],
            words=words,
            reply=reply,
            status='queued' #This is the typical Twilio api response.
        )

def lookup_reply(recipient):
    return Log.objects.filter(recipient=recipient).first().reply

def pluck_variables(string):
    """
    This will read the broadcast and show which columns
    will need to be provided from the csv.
    """
    environment = Environment(loader=BaseLoader(), 
        block_start_string='@@',
        block_end_string='@@',
        variable_start_string='[[',
        variable_end_string=']]')
    
    parsed = environment.parse(string)

    return meta.find_undeclared_variables(parsed)

def render_sms_template(string, context):
    """
    This is pluck the variables from the csv and render the
    given template per text with the variables.
    """
    environment = Environment(loader=BaseLoader(), 
        block_start_string='@@',
        block_end_string='@@',
        variable_start_string='[[',
        variable_end_string=']]')

    template = environment.from_string(string)

    return template.render(**context)