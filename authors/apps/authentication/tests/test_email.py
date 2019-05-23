from django.test import TestCase
from django.urls import reverse
from rest_framework import test, status
from ..models import User
from authors.apps.authentication.jwt_generator import jwt_encode
from authors.apps.core.utils import send_verification_email


class EmailTest(TestCase):
    def setUp(self):
        self.client = test.APIClient()
        self.data = {
                "user": {
                    "email": "tester3@mail.com",
                    "username": "tester3",
                    "password": "tester321"
                }
                }

    def test_user_not_verified_on_create(self):
        self.client.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "tester@mail.com",
                    "username": "tester",
                    "password": "tester1234"
                }
            },
            format="json"
        )
        test_user = User.objects.get(email="tester@mail.com")
        self.assertFalse(test_user.is_verified)

    def test_email_sent(self):
        response = send_verification_email(
            'authorshaven23@gmail.com',
            'yt@yopmail.com',
            'Please verify mail', '<p>hello sir<p>'
        )
        self.assertTrue(response.status_code == 202)

    def test_error_email_not_sent(self):
        response = send_verification_email(
            'authorshaven23@gmail.com',
            'to', '', '<p>outhors</p>')
        self.assertFalse(response)

    def test_verification_success_if_user_passes_valid_token(self):
        """
        Users should be able to verify their account if they
        pass a valid token
        """

        self.client.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "tester3@mail.com",
                    "username": "tester",
                    "password": "tester1234"
                }
            },
            format="json"
        )

        token = jwt_encode('tester3@mail.com')
        res = self.client.get(
            reverse('authentication:email verification', args=(token,)))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
