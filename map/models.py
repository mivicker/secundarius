import json
from decimal import Decimal
import urllib.parse
from django.db import models
import requests


def geocode(address):
    """
    Returns lattitude and longitude for a provided address.
    """
    base_url = "https://nominatim.openstreetmap.org/"
    
    safe_address = urllib.parse.quote(address)
    query_template = f"search.php?q={safe_address}&format=jsonv2"

    response = requests.get(base_url + query_template)

    data = json.loads(response.content)
    try:
        return (Decimal(data[0]["lat"]), Decimal(data[0]["lon"]))
    except IndexError:
        return Decimal('NaN'), Decimal('NaN')


class Location(models.Model):
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2, default="MI")
    zip_code = models.CharField(max_length=5)
    latitude = models.FloatField(blank=True, null=True, editable=False)
    longitude = models.FloatField(blank=True, null=True, editable=False)
    
    @property
    def address(self):
        return f"{self.street_address}, {self.city}, {self.state} {self.zip_code}"

    def save(self, *args, **kwargs):
        if not self.latitude or self.longitude:
            self.latitude, self.longitude = geocode(self.address)
        super().save(*args, **kwargs)
    

    def __str__(self):
        return self.address


class Partner(models.Model):
    name = models.CharField(max_length=75)
    short_name = models.CharField(max_length=75)

    def __str__(self):
        return self.name


class Site(models.Model):
    name = models.CharField(max_length=75)
    partner = models.ForeignKey(Partner, on_delete=models.SET_NULL, null=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    referral_types = (
        ("PR", "Priority"), # assign to nearest of these hubs if in range
        ("SD", "Secondary"), # assign to nearest of these hubs if not in range of pr hub
        ("RF", "Referral"), # notify agent to refer client to this agency
        ("IN", "Inert"), # not available for referrals, but would like to map.
    )
    referral_type = models.CharField(max_length=2, choices=referral_types)

    def as_dict(self):
        return {
            "name": self.name,
            "partner": self.partner.name,
            "address": self.location.address,
            "lat": self.location.latitude,
            "lng": self.location.longitude,
        }

    def __str__(self):
        return self.name



