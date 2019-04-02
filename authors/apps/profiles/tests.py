from django.test import TestCase
from rest_framework import test, status


class ProfileTest(TestCase):

    def test_profile_created_on_signup(self):
        pass

    def test_get_profile(self):
        pass

    def test_profile_fields_valid(self):
        # Check that the profile contains a timestamp, bio and image
        pass

    def test_profile_update_valid_values(self):
        pass

    def test_profile_update_invalid_values(self):
        pass

    def test_profile_update_unauthorized(self):
        pass
