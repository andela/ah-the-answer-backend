from django.test import TestCase
from django.urls import reverse
from rest_framework import test, status

class SocialAuthTest(TestCase):
    def setUp(self):
        self.client = test.APIClient()

    # FACEBOOK
    def test_user_signup_page_redirects_to_facebook(self):
        """
            Ensures that the redirects are found, basically tests
            that the configurations are functional
        """
        res = self.client.get(
            reverse('social:begin', kwargs={'backend': 'facebook'}))
        self.assertEqual(res.status_code, status.HTTP_302_FOUND) 

    # Github
    def test_user_signup_page_redirects_to_github(self):
        """
            Ensures that the redirects are found, basically tests
            that the configurations are functional
        """
        res = self.client.get(
            reverse('social:begin', kwargs={'backend': 'github'}))
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)

    # GOOGLE
    def test_user_signup_page_redirects_to_google(self):
        """
            Ensures that the redirects are found, basically tests
            that the configurations are functional
        """
        res = self.client.get(
            reverse('social:begin', kwargs={'backend': 'google-oauth2'}))
        self.assertEqual(res.status_code, status.HTTP_302_FOUND)
