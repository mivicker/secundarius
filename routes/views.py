from django.shortcuts import render
from .henrys_helpers import (create_route_list, string_box, 
    route_num_to_letter, make_pick_list, validate_arguments)
from .fulfillment_helper import create_order_dictionary

def home(request):
	word = 'hot dog'
	if request.method == 'POST':
		word = 'taco'
	return render(request, 'routes/routes.html', {'key_words': word})