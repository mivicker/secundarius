import os
import json

from returns.pipeline import is_successful
from secundarius.settings import BASE_DIR
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from map.models import Site, cached_geocode, suggest_site
from django.http import JsonResponse


@login_required
def serve_sites(_):
    response = {"sites": [site.as_dict() for site in Site.objects.all()]}
    return JsonResponse(response)


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


@login_required
def site_finder(request):
    return render(request, "map/find_site.html")


@csrf_exempt
def calc_best(request):
    address = json.loads(request.body)["address"]
    coords = cached_geocode(address)

    if not is_successful(coords):
        return JsonResponse({
            "status": "SEARCH FAILED",
            "message": "Unable to locate address."
        })

    site = suggest_site(coords.unwrap())

    if site is not None:
        return JsonResponse({
            "status": "SUCCESS",
            "message": site.name,
            "referral_type": site.referral_type
        })

    return JsonResponse({
        "status": "NO HUB",
        "message": "No delivery hub within range."
    })

