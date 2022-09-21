from decimal import Decimal
from django.test import TestCase
from returns.pipeline import is_successful
from map.models import (
    Address,
    Location,
    Partner,
    Site,
    cached_geocode,
    find_location,
    geocode_address,
    location_from_address,
    parse_address,
    suggest_site,
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
        coords = geocode_address(self.test_address).unwrap()
        self.assertAlmostEqual(coords.lat, self.correct_lat)
        self.assertAlmostEqual(coords.lng, self.correct_lng)

    def test_parse_address(self):
        expected = Address(
            street_address="2131 Beaufait St",
            city="Detroit",
            state="MI",
            zip_code="48207",
        )
        result = parse_address(self.test_address).unwrap()

        self.assertEqual(result, expected)

    def test_find_location(self):
        address = Address(
            street_address="2131 Beaufait St",
            city="Detroit",
            state="MI",
            zip_code="48207",
        )

        location = find_location(address).unwrap()

        self.assertEqual(location, self.test_location)

    def test_cached_geocode(self):
        coords = cached_geocode(self.test_address).unwrap()

        self.assertAlmostEqual(coords.lat, self.correct_lat)
        self.assertAlmostEqual(coords.lng, self.correct_lng)
        self.assertTrue(coords.cached)


class TestDispatch(TestCase):
    def setUp(self):
        locations = [
            ("PR", "2131 Beaufait St, Detroit, MI 48207"),
            ("PR", "21495 Trolley Industrial Drive, Taylor, MI 48180"),
            ("SD", "23401 Jefferson Ave, St Clair Shores, MI 48080"),
            ("SD", "8642 Woodward Ave, Detroit, MI 48202"),
            ("RF", "4643 Moran St, Detroit, MI 48207"),
            ("RF", "34850 Marquette St, Westland, MI 48185"),
            ("IN", "5454 Venoy Rd, Wayne, MI 48184"),
        ]

        partner = Partner.objects.create(
            name="no partner name", short_name="nopartnername"
        )

        self.sites = [
            Site.objects.create(
                name=f"site {i}",
                partner=partner,
                location=location_from_address(parse_address(address).unwrap()),
                referral_type=referral_type,
            )
            for i, (referral_type, address) in enumerate(locations)
        ]

    def test_primary_closest(self):
        # test address in two primary zones goes to closest
        coords = cached_geocode("6544 Grandmont Ave, Detroit MI, 48228").unwrap()
        suggested = suggest_site(coords)
        if suggested is None:
            self.fail()

        self.assertEqual(suggested.name, "site 1")

    def test_primary_over_secondary(self):
        # test address in primary zone and secondary zone
        #    goes to primary even if secondary is closer
        coords = cached_geocode("1965 Country Club Dr, Grosse Pointe Woods, MI 48236").unwrap()
        suggested = suggest_site(coords)
        if suggested is None:
            self.fail()

        self.assertEqual(suggested.name, "site 0")

    def test_secondary_closest(self):
        # test address in two secondary zones goes to closest
        coords = cached_geocode("1965 Country Club Dr, Grosse Pointe Woods, MI 48236")
        if not is_successful(coords):
            self.fail()

        suggested = suggest_site(coords.unwrap())
        
        if suggested is None:
            self.fail()

        self.assertEqual(suggested.name, "site 0")

    def test_referral_and_secondary(self):
        # test that address closer to referral address goes there before secondary
        pass

    def test_address_outside_zone(self):
        # test if address is in no zone fails gracefully
        coords = cached_geocode("814 Bentley Dr, Monroe, MI 48162").unwrap()
        suggested = suggest_site(coords)

        if suggested is not None:
            self.fail()

    def deliver_correct_fail_message(self):
        # Make sure that we know if error happened with geocode
        # or with not finding zone.
        pass


