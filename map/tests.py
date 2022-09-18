from decimal import Decimal
from django.test import TestCase
from map.models import (
    Address,
    Location,
    cached_geocode,
    find_location,
    geocode,
    parse_address,
)


class TestGeocode(TestCase):
    def setUp(self) -> None:
        self.test_address = "2131 Beaufait St, Detroit, MI 48207"
        self.test_location = Location.objects.create(
            street_address="2131 Beaufait St",
            city="Detroit",
            state="MI",
            zip_code="48207",
        )
        self.correct_lat = Decimal("42.35422095")
        self.correct_lng = Decimal("-83.01419965263585")

        return super().setUp()

    def test_geocode(self):
        lat, lng = geocode(self.test_address)
        self.assertAlmostEqual(lat, self.correct_lat)
        self.assertAlmostEqual(lng, self.correct_lng)

    def test_parse_address(self):
        expected = Address(
            street_address="2131 Beaufait St",
            city="Detroit",
            state="MI",
            zip_code="48207",
        )
        result = parse_address(self.test_address)

        self.assertEqual(result, expected)

    def test_find_location(self):
        address = Address(
            street_address="2131 Beaufait St",
            city="Detroit",
            state="MI",
            zip_code="48207",
        )

        location = find_location(address)

        self.assertEqual(location, self.test_location)

    def test_cached_geocode(self):
        coords = cached_geocode(self.test_address)

        self.assertAlmostEqual(coords.lat, self.correct_lat)
        self.assertAlmostEqual(coords.lng, self.correct_lng)
        self.assertTrue(coords.cached)

