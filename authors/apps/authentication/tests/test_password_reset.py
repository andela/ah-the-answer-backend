from django.test import TestCase
from rest_framework import test, status
from django.urls import reverse
from ..models import User


class PasswordResetTest(TestCase):
    def setUp(self):
        pass

    def test_password_reset_request(self):
        pass

    def test_password_reset_email_non_existent(self):
        pass

    def test_password_reset_email_missing_request(self):
        pass

    def test_password_reset_email_invalid_pattern(self):
        pass
