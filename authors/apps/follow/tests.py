from django.test import TestCase
from django.test import Client
from django.urls import reverse
from rest_framework import test, status
import io
from rest_framework.test import APIClient

from .models import Follows
from ..authentication.models import User


class TestFollowViews(TestCase):
    """Tests the views contained in the 'follow' app"""
    def setUp(self):

        """Create, authenticate and login first user"""
        self.client_1 = APIClient()
        self.user_1 = self.client_1.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "demo@mail.com",
                    "username": "Bob",
                    "password": "Bob12345"
                }
            },
            format="json"
        )
        test_user_1 = User.objects.get(username='Bob')
        test_user_1.is_verified = True
        test_user_1.save()
        self.login_1 = self.client_1.post(
            reverse('authentication:user-login'),
            data={
                "user": {
                    "email": "demo@mail.com",
                    "password": "Bob12345"
                }
            },
            format="json"
        )
        # self.token_1 = self.login_1.data['token']
        # self.client_1.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        """Create, authenticate and login second user"""
        self.client_2 = APIClient()
        self.user_2 = self.client_2.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "mail@demo.com",
                    "username": "Mary",
                    "password": "Mary12345"
                }
            },
            format="json"
        )
        test_user_2 = User.objects.get(username='Mary')
        test_user_2.is_verified = True
        test_user_2.save()
        self.login_2 = self.client_2.post(
            reverse('authentication:user-login'),
            data={
                "user": {
                    "email": "mail@demo.com",
                    "password": "Mary12345"
                }
            },
            format="json"
        )
        # self.token_2 = self.login_2.data['token']
        # self.client_2.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

        def test_user_attempts_to_follow_themselves(self):
            self.token_1 = self.login_1.data['token']
            self.client_1.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
            response = self.client_1.post(reverse('follow:follow-user'), args=['Bob'], format="json")
            self.assertEqual(response.status_code, "Cheese")