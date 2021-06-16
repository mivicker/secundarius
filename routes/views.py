from django.shortcuts import render

def home(request):
	word = 'hot dog'
	if request.method == 'POST':
		word = 'taco'
	return render(request, 'routes/routes.html', {'key_words': word})