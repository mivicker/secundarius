from django import forms
from .models import Broadcast, Reply
from .validators import validate_upload_dict

class UploadFileForm(forms.Form):
    file = forms.FileField(widget=forms.FileInput(
        attrs=({'id': 'upload-csv'})),validators=[validate_upload_dict])

class UpdateBroadcastForm(forms.ModelForm):
    class Meta:
        model = Broadcast
        fields = ['words']

class UpdateReplyForm(forms.ModelForm):
    class Meta:
        model = Reply
        fields = ['words']