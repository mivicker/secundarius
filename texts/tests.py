import os
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import Mock, call
from .views import send_each, read_csv
from .models import Broadcast, Log

class SendViewTest(TestCase):
    def setUp(self):
        self.fixtures_dir =  os.path.join(
            os.path.dirname(__file__), 'fixtures')
        self.recipients_dict = [
            {'Member ID': '1', 
            'First Name': 'Harvey', 
            'Phone Number': '17342775603'},
            {'Member ID': '2',
            'First Name': 'Ruth',
            'Phone Number': '17344266718'},
            {'Member ID': '3',
            'First Name': 'Susu',
            'Phone Number': '17344265729'}
        ]
        self.recipients_csv = [
            'Member ID, First Name, Phone Number',
            '1,Harvey,17342775603',
            '2,Ruth,17344266718',
            '3,Susu,17344265729'
        ]

    def test_read_csv(self):
        """
        Reads a csv into a dictionary.
        """
        file = SimpleUploadedFile('recipients.csv', 
            '\n'.join(self.recipients_csv).encode('utf-8'), 
            content_type="csv")
        
        recipients_dict = read_csv(file)

        recipients_dict == self.recipients_dict

    def test_send_each(self):
        """
        This feels a little like testing implementation,
        but the goal of this func is to hit the twilio api.
        """
        fake_twilio = Mock()
        words = Broadcast.objects.create(words="This is the text sent out.")
        calls = [call.messages.create(
                body=words.words, 
                from_='+13132514241', 
                to=recipient['Phone Number']) 
            for recipient in self.recipients_dict]

        texts = send_each(words, self.recipients_dict, fake_twilio)

        self.assertEqual(len(Log.objects.all()), len(calls))
        fake_twilio.assert_has_calls(calls)