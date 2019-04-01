from django.test import TestCase
from django.test import Client

from .models import Profile
from authentication.models import User


class TestProfileModel(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="Bob",
            email="demo@mail.com",
            password="123"
        )

    def test_profile_user_relation(self):
        u = self.user
        profile = Profile(user=u, user_bio="Biography", name="Bobby Doe")
        profile.save()
        username = profile.user.username
        self.assertEqual(username, "Bob")
