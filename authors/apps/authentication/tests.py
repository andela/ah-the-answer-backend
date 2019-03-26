from django.test import TestCase
from django.urls import reverse
from django.conf import settings
from rest_framework.test import APIClient
from django.contrib.auth.models import User
import jwt
import datetime


class UserLoginTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            username="Test",
            password="test123",
            email="test@mail.com"
        )
        self.token = jwt.encode({
            "user_id": self.user.id,
            "exp": datetime.datetime.utcnow().datetime.timedelta(days=1)
        }, settings.SECRET_KEY, algorithm='HS256')
