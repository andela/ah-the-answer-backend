from django.test import TestCase
from django.test import Client
from django.urls import reverse
from rest_framework import test, status
import io
from rest_framework.test import APIClient

from .models import Profile
from ..authentication.models import User

class TestModelCreate(TestCase):
    """Tests the whether model can create a new record"""

    def setUp(self):
        user = User.objects.create(username="johndoe")
        self.user_bio = "Was asked to produce a bribe to get the service"
        self.name = "John Doe"
        self.number_followers = 67
        self.number_followings = 56
        self.total_articles = 88

        self.record = Profile(
            user_bio = self.user_bio,
            name = self.name,
            number_followers = self.number_followers,
            number_followings = self.number_followings,
            total_articles = self.total_articles,
            user = user
        )

    def test_model_can_create_record(self):
        """Test whether model can create a record"""
        initial = Profile.objects.count()
        self.record.save()
        updated = Profile.objects.count()

        self.assertNotEqual(initial, updated)

class TestModelCase(TestCase):
    """Tests the whether model can create a new record"""

    def setUp(self):
        """This setup creates and logs in a new user. After login the user
        receives an auth token that is stored and will be used to access the
        protected views contained in this test series. Lastly, two mock profile
        sets for a user are made: the first being valid,
        the second being invalid."""
        self.client = APIClient()
        self.user = self.client.post(
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
        self.login = self.client.post(
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
                                   "user_bio": "My life story",
                                   "name": "Bobby Doe",
                                   "number_followers": 100,
                                   "number_following": 50,
                                   "total_article": 500
                               }
                               }
        self.user_profile_2 = {"profile":
                               {
                                   "game": "Bobby Doe",
                                   "number_followers": 100,
                                   "number_following": 50,
                                   "total_article": 500
                               }
                               }
        self.token = self.login.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)


    def test_user_can_edit_profile(self):
        """
        This test case tests that an authenticated
        user can edit their own profile
        """

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
        """
        This test case tests that an authenticated
        user cannot upload an empty file field of their own profile
        """
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
            reverse('profiles:profile-image',
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
        Creates a dummy, temporary image for testing purposes
        Returns a new temporary image file
        """
        import tempfile
        from PIL import Image

        image = Image.new('RGB', (100, 100))
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file, 'jpeg')
        # important because after save(),
        # the fp is already at the end of the file
        tmp_file.seek(0)  # retrieves the created temp file
        return tmp_file

    def test_image_upload_successful(self):
        """
        This test case tests that an authenticated
        user can update their own profile avatar
        """
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
            reverse('profiles:profile-image',
                    kwargs={'username': User.objects.get().username}),
            data={
                "avatar": self.temporary_image
            },
            format='multipart'
        )
        self.assertEquals(res.status_code, status.HTTP_200_OK)

    def test_create_profile(self):
        """Test if the 'create profile' view is able to successfully
        create a new user profile."""
        response = self.client.post(reverse('profile:profile-create'),
                                    self.user_profile_1, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['success'],
                         "Profile for 'Bob' created successfully")

    def test_fetch_user_profile(self):
        """Creates a user profile and then tests if the 'get profile' view is
        able to successfully fetch stored user profile data."""
        response = self.client.post(reverse('profile:profile-create'),
                                    self.user_profile_1, format="json")
        response = self.client.get(reverse('profile:profile-fetch',
                                           args=['Bob']), format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['profile']['username'], "Bob")
        self.assertEqual(response.data['profile']['name'], "Bobby Doe")

    def test_fetch_invalid_profile(self):
        """Attempt to fetch a user profile that does not exist."""
        response = self.client.get(reverse('profile:profile-fetch',
                                           args=['Bob']), format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_invalid_profile(self):
        """Attempt to create a user profile with invalid data."""
        response = self.client.post(reverse('profile:profile-create'),
                                    self.user_profile_2, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
