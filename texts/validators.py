from .models import Broadcast
from django import forms
from django.core.files import File
from django.utils.translation import gettext as _ # This is for translation
from .logic import read_csv, pluck_variables


def validate_upload_dict(file:File):
    dictionaries = read_csv(file.read().decode('UTF-8'))
    current_broadcast:Broadcast = Broadcast.objects.first()
    for fill_field in pluck_variables(current_broadcast.words):
       if any(fill_field not in dictionary for dictionary in dictionaries):
           raise forms.ValidationError(_("CSV row is missing a field value."),
                                       code="bad-columns")
