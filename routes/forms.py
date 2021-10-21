import datetime
from django import forms


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
