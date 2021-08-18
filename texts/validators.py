from .models import Broadcast
from django import forms
from django.utils.translation import gettext as _ # This is for translation
from .handlers import read_csv

def validate_upload_dict(file):
    dictionaries = read_csv(file)
    current_broadcast = Broadcast.objects.first()
    for fill_field in current_broadcast.fillfield_set.all():
       if any(fill_field.field_name not in dictionary for dictionary in dictionaries):
           raise forms.ValidationError(_("CSV row is missing an field value."), code="bad-columns")