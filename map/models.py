from dataclasses import dataclass, asdict
import json
from decimal import Decimal
from typing import Optional, Tuple
import urllib.parse
from django.db import models
import requests
from geopy import distance


@dataclass
class Address:
    street_address: str
    city: str
    state: str
    zip_code: str

    def assemble(self):
        f"{self.street_address}, {self.city}, {self.state} {self.zip_code}"


def parse_address(address: str) -> Optional[Address]:
    try:
        street_address, city, state_zip = address.split(",")
        state, zip_code = state_zip.strip().split(" ")

        return Address(
            street_address=street_address,
            city=city.strip(),
            state=state,
            zip_code=zip_code,
        )
    except ValueError:
        return None


def geocode(address) -> Tuple[Decimal, Decimal]:
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
    longitude= models.FloatField(blank=True, null=True, editable=False)
    
    @property
    def address(self):
        return f"{self.street_address}, {self.city}, {self.state} {self.zip_code}"

    @property
    def coords(self) -> Tuple[Decimal, Decimal]:
        return (Decimal(self.latitude), Decimal(self.longitude))

    def save(self, *args, **kwargs):
        if not self.latitude or self.longitude:
            self.latitude, self.longitude = geocode(self.address)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.address


def find_location(address: Address) -> Optional[Location]:
    locations = Location.objects.filter(
        **asdict(address)
    )

    if not locations:
        return None

    return locations[0]


def cached_geocode(address_string: str) -> Tuple[Decimal, Decimal]:
    if (address := parse_address(address_string)) is not None:
        if (location := find_location(address)) is not None:
            return location.coords

    return geocode(address_string)


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


def calc_site_distances(address_coords: Tuple[Decimal, Decimal]):
    """
    Return sites < 10 miles away from address.
    """
    return [
        (site, distance.distance(site.location.coords, address_coords))
        for site in Site.objects.all()
    ]


def suggest_site(coords: Tuple[Decimal, Decimal]) -> Optional[Site]:
    distances = calc_site_distances(coords)
    available = [site for site, distance in distances 
                 if ((distance.miles < 10) & (site.referral_type in ["PR", "SD", "RF"]))]
    if not available:
        return None

    # Check for priority sites first.
    for site in available:
        if site.referral_type == "PR":
            return site

    # If no priority sites, provide closest
    return available[0]

# [zelphias, gleaners - taylor, senior alliance] -> gleaners - taylor
# [senior alliance, zelphias] -> zelphias

