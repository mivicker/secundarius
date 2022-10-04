from dataclasses import dataclass, asdict
import json
from decimal import Decimal
from typing import Optional, Tuple
import urllib.parse
from django.db import models
import requests
from geopy import distance
from returns.result import Failure, Result, Success, safe
from returns.pipeline import flow, is_successful
from returns.pointfree import bind


@dataclass
class Coords:
    lat: Decimal
    lng: Decimal
    cached: bool = False

    @property
    def coords(self):
        return (self.lat, self.lng)


@dataclass
class Address:
    street_address: str
    city: str
    state: str
    zip_code: str

    def assemble(self):
        f"{self.street_address}, {self.city}, {self.state} {self.zip_code}"


class BadAddressString(Exception):
    pass


def parse_address(address: str) -> Result[Address, Exception]:
    try:
        street_address, city, state_zip = address.split(",")
        state, zip_code = state_zip.strip().split(" ")

        return Success(Address(
            street_address=street_address,
            city=city.strip(),
            state=state,
            zip_code=zip_code,
        ))
    except ValueError:
         return Failure(BadAddressString())


@safe
def make_geocode_request(address_str: str) -> requests.Response:
    base_url = "https://nominatim.openstreetmap.org/"
    safe_address = urllib.parse.quote(address_str)
    query_template = f"search.php?q={safe_address}&format=jsonv2"
    response = requests.get(base_url + query_template)
    response.raise_for_status()

    return response


@safe
def parse_json(response: requests.Response) -> Coords:
    data = json.loads(response.content)
    return Coords(
        lat = Decimal(data[0]["lat"]), 
        lng = Decimal(data[0]["lon"])
    )


def geocode_address(address_string: str) -> Result[Coords, Exception]:
    return flow(
        address_string,
        make_geocode_request,
        bind(parse_json),
    )


def cached_geocode(address_string: str) -> Result[Coords, str]:
    location: Result = flow(
        address_string,
        parse_address,
        bind(find_location)
    )
    if is_successful(location):
        return Success(location.unwrap().coords)

    coords = geocode_address(address_string)
    if is_successful(coords):
        return Success(coords.unwrap())

    return Failure("Could not geocode address")


class Location(models.Model):
    street_address = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=2, default="MI")
    zip_code = models.CharField(max_length=5)
    latitude = models.FloatField(blank=True, null=True, editable=False)
    longitude = models.FloatField(blank=True, null=True, editable=False)

    @property
    def address(self):
        return (
            f"{self.street_address}, {self.city}, {self.state} {self.zip_code}"
        )

    @property
    def coords(self) -> Coords:
        return Coords(
            lat=Decimal(self.latitude), 
            lng=Decimal(self.longitude),
            cached=True,
        )

    def save(self, *args, **kwargs):
        if not self.latitude or self.longitude:
            coords = cached_geocode(self.address).unwrap()
            self.latitude = coords.lat
            self.longitude = coords.lng
        super().save(*args, **kwargs)

    def __str__(self):
        return self.address


def find_location(address: Address) -> Result[Location, str]:
    locations = Location.objects.filter(**asdict(address))
    if locations.exists():
        return Success(locations[0])
    return Failure("Location not found")


def location_from_address(address: Optional[Address]) -> Optional[Location]:
    if not address:
        return
    return Location.objects.create(**asdict(address))


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
        ("PR", "Priority"),  # assign to nearest of these hubs if in range
        ("SD", "Secondary"),  # assign to these hubs if not in range of pr hub
        ("RF", "Referral"),  # notify agent to refer client to this agency
        ("IN", "Inert"),  # not available for referrals, but would like to map.
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


def calc_site_distances(address_coords: Coords):
    """
    Return sites < 10 miles away from address.
    """
    return [
        (site, distance.distance(site.location.coords.coords, address_coords.coords))
        for site in Site.objects.all()
    ]


def suggest_site(coords: Coords) -> Optional[Site]:
    distances = calc_site_distances(coords)
    arranged = sorted(distances, key=lambda x: x[1])
    available = [
        site
        for site, distance in arranged
        if ((distance.miles < 9) & (site.referral_type in ["PR", "SD", "RF"]))
    ]
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
