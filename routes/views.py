from django.shortcuts import render

def home(request):
	if request.method == 'POST':
		context = {'message': 'bad things'}
	else:
		context = {'message': 'nothing'}
	return render(request, 'routes/routes.html', context)