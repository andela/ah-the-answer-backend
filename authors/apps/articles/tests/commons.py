from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.test import TestCase
from rest_framework import test, status
from ..models import ReviewsModel, Article
from authors.apps.authentication.models import User


class BaseSetup(TestCase):

    def setUp(self):
        """
        This setup creates and logs in a new user. After login the user
        receives an auth token that is stored and will be used to access the
        protected views contained in this test series. Lastly, two mock profile
        sets for a user are made: the first being valid,
        the second being invalid.
        """
        self.client = APIClient()
        self.client2 = APIClient()
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
        self.user2 = self.client2.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "pete@mail.com",
                    "username": "Pete",
                    "password": "Pete12345"
                }
            },
            format="json"
        )
        test_user = User.objects.get(username="Bob")
        test_user.is_verified = True
        test_user.save()
        test_user2 = User.objects.get(username="Pete")
        test_user2.is_verified = True
        test_user2.save()
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
        self.login2 = self.client2.post(
            reverse('authentication:user-login'),
            data={
                "user": {
                    "email": "pete@mail.com",
                    "password": "Pete12345"
                }
            },
            format="json"
        )
        self.token = self.login.data['token']
        self.token2 = self.login2.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.client2.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token2)

    def post_article(self):
        return self.client.post(
            reverse('articles:create-list'),
            data={
                "article": {
                    "title": "Test title",
                    "body": "This is a very awesome article on testing tests",
                    "description": "Written by testing tester",
                }
            },
            format="json"
        )

    def post_review(self):
        return self.client2.post(
            reverse('articles:review', kwargs={
                "slug": Article.objects.get().slug
            }),
            data={
                "review": {
                    "review_body": "I really liked the article",
                    "rating_value": 5
                }
            },
            format="json"
        )
