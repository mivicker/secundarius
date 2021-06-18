from django import forms
from .models import Words

class UploadFileForm(forms.Form):
	file = forms.FileField(widget=forms.FileInput(
		attrs=({'id': 'upload-csv'})))

class UpdateWordsForm(forms.ModelForm):
	class Meta:
		model = Words
		fields = ['words']	