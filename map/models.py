import json
from decimal import Decimal
import urllib.parse
from django.db import models
from django.conf import settings
import requests


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
            self.latitude, self.longitude = self.geocode(self.address)
        super().save(*args, **kwargs)
    
    @staticmethod
    def geocode(address):
        """
        Returns lattitude and longitude for a provided address.
        """

        with open(settings.key) as f:
            secrets = json.load(f)
        gmaps_base_url = "https://maps.googleapis.com/maps/api/geocode/json/"
        query_string = urllib.parse.urlencode({"address": address, "key": secrets["GMAPS_KEY"]})
        maps_uri = f"{gmaps_base_url}?{query_string}"
        response = requests.get(maps_uri)
        data = json.loads(response.content)
        if data["status"] == "OK":
            lat = data['results'][0]['geometry']['location']['lat']
            lng = data['results'][0]['geometry']['location']['lng']

        return Decimal(lat), Decimal(lng)


class Partner(models.Model):
    name = models.CharField(max_length=75)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)

