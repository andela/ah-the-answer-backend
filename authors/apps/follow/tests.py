from django.test import TestCase
from django.test import Client
from django.urls import reverse

from rest_framework import test, status
from rest_framework.test import APIClient

import io

from .models import Follows
from ..authentication.models import User


class TestFollowViews(TestCase):
    """Tests the views contained in the 'follow' app"""
    def setUp(self):

        """Create, authenticate and login first user. Also creates
        a profile."""
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
        self.user_profile_1 = {"profile":
                               {
                                   "user_bio": "Doing the right thing!",
                                   "name": "Bobby Doe",
                                   "number_followers": 0,
                                   "number_following": 0,
                                   "total_article": 0
                               }
                               }

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

    def test_user_attempts_to_follow_themselves(self):
        self.token_1 = self.login_1.data['token']
        self.client_1.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_1)
        response = self.client_1.post(reverse('follow:follow-user',
                                      args=['Bob']), format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "User is attempting to "
                         "follow themselves. This is not allowed.")

    def test_user_follows_other_user(self):
        self.token_1 = self.login_1.data['token']
        self.client_1.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_1)
        response = self.client_1.post(reverse('follow:follow-user',
                                      args=['Mary']), format="json")
        self.assertEqual(response.data['success'], "Now following Mary.")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_attempts_to_follow_same_user_twice(self):
        self.token_1 = self.login_1.data['token']
        self.client_1.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_1)
        response = self.client_1.post(reverse('follow:follow-user',
                                      args=['Mary']), format="json")
        response = self.client_1.post(reverse('follow:follow-user',
                                      args=['Mary']), format="json")
        self.assertEqual(response.data['error'], "User already followed.")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_attempts_to_follow_non_existent_user(self):
        self.token_1 = self.login_1.data['token']
        self.client_1.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_1)
        response = self.client_1.post(reverse('follow:follow-user',
                                      args=['John']), format="json")
        self.assertEqual(response.data['error'], 'Unable to create a '
                         'following. This user does not exist. Please choose '
                         'another user.')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_user_follows(self):
        self.token_1 = self.login_1.data['token']
        self.client_1.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_1)
        self.client_1.post(reverse('follow:follow-user', args=['Mary']),
                           format="json")
        response = self.client_1.get(reverse('follow:list-followers',
                                     args=['Mary']), format="json")
        self.assertEqual(response.data['followers'][0],
                         'Bob')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_unfollows_user(self):
        self.token_1 = self.login_1.data['token']
        self.client_1.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_1)
        self.client_1.post(reverse('follow:follow-user', args=['Mary']),
                           format="json")
        self.client_1.delete(reverse('follow:unfollow-user', args=['Bob',
                             'Mary']), format="json")
        response = self.client_1.get(reverse('follow:list-followings',
                                     args=['Bob']), format="json")
        self.assertEqual(response.data['followed_users'], [])

    def test_user_attempts_to_unfollow_unfollowed_user(self):
        self.token_1 = self.login_1.data['token']
        self.client_1.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_1)
        response = self.client_1.delete(reverse('follow:unfollow-user',
                                        args=['Bob', 'Mary']), format="json")
        self.assertEqual(response.data['error'], 'You do not follow Mary. '
                         'Unfollow failed.')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_attempts_to_unfollow_as_another_user(self):
        self.token_1 = self.login_1.data['token']
        self.client_1.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_1)
        response = self.client_1.delete(reverse('follow:unfollow-user',
                                        args=['Mary', 'Bob']), format="json")
        self.assertEqual(response.data['error'], 'Incorrect user logged in.'
                         ' Check username in the URL.')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_user_stats(self):
        self.token_1 = self.login_1.data['token']
        self.client_1.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_1)
        self.client_1.post(reverse('profile:profile-create'),
                           self.user_profile_1, format="json")
        self.client_1.post(reverse('follow:follow-user', args=['Mary']),
                           format="json")

        self.token_2 = self.login_2.data['token']
        self.client_2.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_2)
        self.client_2.post(reverse('follow:follow-user', args=['Bob']),
                           format="json")
        response = self.client_1.get(reverse('follow:count-follows',
                                     args=['Bob']), format="json")
        self.assertEqual(response.data['success'][0]['follows'], 1)
        self.assertEqual(response.data['success'][1]['followers'], 1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_attempt_to_get_user_stats_for_nonexistent_user(self):
        response = self.client_1.get(reverse('follow:count-follows',
                                     args=['John']), format="json")
        self.assertEqual(response.data['error'], "This given username does "
                         "not have an Author's Haven account.")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
