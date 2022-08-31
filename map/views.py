import os
import json
from secundarius.settings import BASE_DIR
from django.contrib.auth.views import login_required
from django.shortcuts import render
from django.http import JsonResponse


@login_required
def show_map(request):
    return render(request, "map/map.html")


@login_required
def place_map(_):
    with open(
        os.path.join(
            BASE_DIR, "map", "static", "data", "Below1point5povertyover55.json"
        )
    ) as f:
        return JsonResponse(json.load(f))
