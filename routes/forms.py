import datetime
from django import forms
from .models import Depot


def next_delivery_day():
    today = datetime.date.today()
    if today.weekday() == 4:
        return (today + datetime.timedelta(days=3))
    if today.weekday() == 5:
        return (today + datetime.timedelta(days=2))
    return today + datetime.timedelta(days=1)


class DateForm(forms.Form):
    date = forms.DateField(widget=forms.SelectDateWidget, 
                           initial=next_delivery_day)


class DepotForm(forms.ModelForm):
    class Meta:
        model = Depot
        fields = ['active_drivers']

def __init__(self, *args, **kwargs):
    super(DepotForm, self).__init__(*args, **kwargs)
    for visible in self.visible_fields():
        visible.field.widget.attrs['class'] = 'select-field'