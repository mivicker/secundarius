import os
from django.shortcuts import render
from .henrys_helpers import (create_route_list, string_box, 
    route_num_to_letter, make_pick_list, validate_arguments)
from .fulfillment_helper import create_order_dictionary

def home(request):
	word = {'This is a test'}
	return render(request, 'routes/routes.html', {'key_words': word})