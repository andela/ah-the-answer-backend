from django.test import TestCase
from rest_framework import test, status
from django.urls import reverse
from ..models import User


class PasswordResetTest(TestCase):
    def setUp(self):
        self.client = test.APIClient()
        self.user = User.objects.create(
            email="test@mail.com",
            username="test",
            password="test1234"
        )

    def test_password_reset_request(self):
        pass
        # response = self.client.post(
        #     reverse('authentication:password-reset'),
        #     data={
        #         "email": "test@mail.com"
        #     }
        # )

        # self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_password_reset_email_non_existent(self):
        pass
        # response = self.client.post(
        #     reverse('authentication:password-reset'),
        #     data={
        #         "email": "testerror@mail.com"
        #     }
        # )

        # self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_password_reset_email_missing_request(self):
        pass

    def test_password_reset_email_invalid_pattern(self):
        pass
