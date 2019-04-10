from django.test import TestCase
from django.urls import reverse
from rest_framework import test, status
from authors.apps.authentication.models import User


class TestUser(TestCase):
    def setUp(self):
        self.client = test.APIClient()
        self.user = self.client.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "user@mail.com",
                    "username": "user",
                    "password": "user1234"
                }
            },
            format="json"
        )
        #verify the user
        test_user = User.objects.get(username='user')
        test_user.is_verified = True
        test_user.save()
        print(User.objects.get(username='user').is_verified)
        self.login = self.client.post(
            reverse('authentication:user-login'),
            data={
                "user": {
                    "email": "user@mail.com",
                    "password": "user1234"
                }
            },
            format="json"
        )
        self.token = self.login.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    def test_gets_user_from_endpoint(self):
        response = self.client.get(
            reverse('authentication:user-details'),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'user@mail.com')

    def test_no_token_get_user(self):
        response = test.APIClient(HTTP_AUTHORIZATION='Bearer' + '').get(
            reverse('authentication:user-details'),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_extra_attributes_get_user(self):
        response = test.APIClient(
            HTTP_AUTHORIZATION='Bearer extras' + self.token
            ).get(
                reverse('authentication:user-details'),
                format="json"
            )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
