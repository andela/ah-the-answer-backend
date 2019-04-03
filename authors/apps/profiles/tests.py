from django.test import TestCase
from django.test import Client

from .models import Profile
from ..authentication.models import User


class TestProfileModel(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username="Bob",
            email="demo@mail.com",
            password="123"
        )

    def test_relation_between_profile_and_user_models(self):
        test_user = self.user
        profile = Profile(user=test_user, user_bio="Biography",
                          name="Bobby Doe")
        profile.save()
        username = profile.user.username
        self.assertEqual(username, "Bob")
