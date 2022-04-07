import datetime
from django import forms
from .models import Warehouse, Invoice


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['substitutions', 'out', 'additions']

    def __init__(self, *args, **kwargs):
        super(WarehouseForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'select-field'


class UploadFileForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(
        attrs=({'id': 'upload-xls'})))


def next_invoice_date():
    last_invoice = Invoice.objects.order_by("pulled_date").last()
    return last_invoice.end_date + datetime.timedelta(days=1)


def default_invoice_end_date():
    return datetime.datetime.now().date()


class StartDateForm(forms.Form):
    date = forms.DateField(widget=forms.SelectDateWidget, 
                           initial=next_invoice_date)


class EndDateForm(forms.Form):
    date = forms.DateField(widget=forms.SelectDateWidget, 
                           initial=default_invoice_end_date)