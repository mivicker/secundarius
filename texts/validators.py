from .models import Broadcast
from django import forms
from django.utils.translation import gettext as _ # This is for translation

def validate_upload_dict(dictionaries):
    current_broadcast = Broadcast.objects.first()
    for field_name in current_broadcast.fillfield_set.all():
        if any(field_name not in dictionary for dictionary in dictionaries):
            raise forms.ValidationError(_("CSV row is missing an field value."), code="bad-columns")