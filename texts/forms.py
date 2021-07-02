from django import forms
from .models import Broadcast, Reply

class UploadFileForm(forms.Form):
	file = forms.FileField(widget=forms.FileInput(
		attrs=({'id': 'upload-csv'})))

class UpdateBroadcastForm(forms.ModelForm):
	class Meta:
		model = Broadcast
		fields = ['words']

class UpdateReplyForm(forms.ModelForm):
	class Meta:
		model = Reply
		fields = ['words']