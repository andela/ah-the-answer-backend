from django.test import TestCase
from django.test import Client
from django.urls import reverse
from rest_framework import test, status
import io
from .models import Profile
from ..authentication.models import User


class TestModelCase(TestCase):
    """Tests the whether model can create a new record"""

    def setUp(self):
        user = User.objects.create(username="johndoe")
        self.user_bio = "This is a test bio"
        self.name = "John Doe"
        self.number_of_followers = 59
        self.number_of_followings = 88
        self.total_articles = 77

        self.profile = Profile(
            user_bio=self.user_bio,
            name=self.name,
            number_of_followers=self.number_of_followers,
            number_of_followings=self.number_of_followings,
            total_articles=self.total_articles,
            user=user
        )

    def test_model_can_create_record(self):
        """Test whether model can create a record"""
        initial = Profile.objects.count()
        self.profile.save()
        updated = Profile.objects.count()

        self.assertNotEqual(initial, updated)


class ViewTestCase(TestCase):
    """Test suite for api views"""

    def setUp(self):
        self.client = test.APIClient()
        self.user_create = self.client.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "username": "johndoe",
                    "email": "johndoe@test.com",
                    "password": "johndoe123"
                }
            },
            format="json"
        )

        self.user = self.client.post(
            reverse('authentication:user-login'),
            data={
                "user": {
                    "email": "johndoe@test.com",
                    "password": "johndoe123"
                }
            },
            format="json"
        )

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.user.data['token'])

    def test_user_can_edit_profile(self):
        create_response = self.client.post(
            reverse('profiles:profile-create'),
            data={
                "profile": {
                    "name": "John Doe",
                    "user_bio": "I work at statefarm",
                    "number_of_followers": 5,
                    "number_of_followings": 6,
                    "total_articles": 45
                }
            },
            format="json"
        )
        self.assertEquals(create_response.status_code, status.HTTP_201_CREATED)
        edit_response = self.client.put(
            reverse('profiles:profile-edit',
                    kwargs={'username': User.objects.get().username}),
            data={
                "profile": {
                    "name": "Mike Mill",
                    "user_bio": "I work at statefarm workhand",
                    "number_of_followers": 5,
                    "number_of_followings": 6,
                    "total_articles": 45
                }
            },
            format="json"
        )
        self.assertEquals(edit_response.status_code, status.HTTP_200_OK)
        self.assertContains(edit_response, "Mike Mill")

    def test_empty_image_upload(self):
        create_response = self.client.post(
            reverse('profiles:profile-create'),
            data={
                "profile": {
                    "name": "John Doe",
                    "user_bio": "I work at statefarm",
                    "number_of_followers": 5,
                    "number_of_followings": 6,
                    "total_articles": 45
                }
            },
            format="json"
        )
        self.assertEquals(create_response.status_code, status.HTTP_201_CREATED)
        res = self.client.patch(
            reverse('profiles:profile-avatar',
                    kwargs={'username': User.objects.get().username}),
            data={
                "profile": {
                    "avatar": " "
                }
            },
            format="json"
        )
        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)

    @property
    def temporary_image(self):
        """
        Returns a new temporary image file
        """
        import tempfile
        from PIL import Image

        image = Image.new('RGB', (100, 100))
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file, 'jpeg')
        # important because after save(), the fp is already at the end of the file
        tmp_file.seek(0)
        return tmp_file

    def test_image_upload_successful(self):
        create_response = self.client.post(
            reverse('profiles:profile-create'),
            data={
                "profile": {
                    "name": "John Doe",
                    "user_bio": "I work at statefarm",
                    "number_of_followers": 5,
                    "number_of_followings": 6,
                    "total_articles": 45
                }
            },
            format="json"
        )
        self.assertEquals(create_response.status_code, status.HTTP_201_CREATED)
        res = self.client.patch(
            reverse('profiles:profile-avatar',
                    kwargs={'username': User.objects.get().username}),
            data={
                "avatar": self.temporary_image
            },
            format='multipart'
        )
        self.assertEquals(res.status_code, status.HTTP_200_OK)

