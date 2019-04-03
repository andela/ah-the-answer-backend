from django.test import TestCase
from django.core import mail
from django.urls import reverse
from rest_framework import test, status
from ..models import User


class EmailTest(TestCase):
    def setUp(self):
        pass

    def test_user_not_verified_on_create(self):
        pass

    def test_email_sent(self):
        pass

    def test_sent_email_content(self):
        pass

    def test_error_email_not_sent(self):
        pass

    def tearDown(self):
        pass
