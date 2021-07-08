import datetime
from django.test import TestCase
from django.urls import reverse
from henrys_helpers import validate_arguments
from sharepointless import get_app_password, load_df_from_sharepoint

class TestHelpers(TestCase):

    def test_validate_arguments_with_arg(self):
        next_day = datetime.datetime.strptime('2021-06-11', '%Y-%m-%d').date() 
        args = ['generate_csv_for_route.py', '2021-06-11']
        self.assertEqual(next_day,validate_arguments(args))

    def test_validate_arguments_without_args(self):
        today = datetime.date.today()
        tomorrow = today + datetime.timedelta(days=3) if today.weekday() == 4 \
            else today + datetime.timedelta(days=1)

        args = ['generate_csv_for_route.py']
        self.assertEqual(tomorrow, validate_arguments(args))

    def test_validate_arguments_invalid_args(self):
        args = ['one', 'two', 'three']
        with self.assertRaises(ValueError): 
            validate_arguments(args)

class TestSharepointless(TestCase):

    def test_get_app_password(self):
        username, password = get_app_password()

        self.assertEqual(username, 'mvickers@gcfb.org')
        self.assertTrue(password)

    def test_load_df_from_sharepoint(self):
        username, password = get_app_password()
        df = load_df_from_sharepoint(
            config.base_url, config.dms_url, 'Constituents', 'All Items', 
            username, password)

        self.assertIn('Member ID', df.columns) 
        self.assertIn('ZIP', df.columns)

    def test_filt_for_day(self):
        pass

    def test_filt_for_future(self):
        pass

class TestViews(TestCase):
    def setUp():
        pass

    def tearDown(self):
        pass

    def delivery_selector_view(self):
        # arrange       
	# act - open page
        response = self.client.get(reverse('delivery-selector'))
	# assert - form loads

    def test_selector_no_input(self):
        # arrange
	# act - post request with no form data
	# assert - that the info from the next business day loads
        pass

    def test_selector_with_input(self):
        pass
