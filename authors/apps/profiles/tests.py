from django.test import TestCase
from django.urls import reverse

from rest_framework import test, status
from rest_framework.test import APIClient

from .models import Profile
from ..authentication.models import User


class TestProfileModel(TestCase):
    def setUp(self):
        """This setup creates and logs in a new user. After login the user
        receives an auth token that is stored and will be used to access the
        protected views contained in this test series. Lastly, two mock profile
        sets for a user are made: the first being valid,
        the second being invalid."""
        self.client = APIClient()
        self.user = self.client.post(
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
        self.login = self.client.post(
            reverse('authentication:user-login'),
            data={
                "user": {
                    "email": "demo@mail.com",
                    "password": "Bob12345"
                }
            },
            format="json"
        )
        self.user_profile_1 = {"profile":
                             {
                                "user_bio": "My life story",
                                "name": "Bobby Doe",
                                "number_followers": 100,
                                "number_following": 50,
                                "total_article": 500
                             }
                             }
        self.user_profile_2 = {"profile":
                             {
                                "game": "Bobby Doe",
                                "number_followers": 100,
                                "number_following": 50,
                                "total_article": 500
                             }
                             }
        self.token = self.login.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_create_profile(self):
        """Test if the 'create profile' view is able to successfully
        create a new user profile."""
        response = self.client.post(reverse('profile:profile-create'),
                                    self.user_profile_1, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['success'], "Profile for 'Bob' created successfully")

    def test_fetch_user_profile(self):
        """Creates a user profile and then tests if the 'get profile' view is
        able to successfully fetch stored user profile data."""
        response = self.client.post(reverse('profile:profile-create'),
                                    self.user_profile_1, format="json")
        response = self.client.get(reverse('profile:profile-fetch',
                                           args=['Bob']), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['profile']['username'], "Bob")
        self.assertEqual(response.data['profile']['name'], "Bobby Doe")

    def test_fetch_invalid_profile(self):
        """Attempt to fetch a user profile that does not exist."""
        response = self.client.get(reverse('profile:profile-fetch',
                                   args=['Bob']), format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_invalid_profile(self):
        """Attempt to create a user profile with invalid data."""
        response = self.client.post(reverse('profile:profile-create'),
                                    self.user_profile_2, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
