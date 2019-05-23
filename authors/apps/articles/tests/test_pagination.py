from django.test import TestCase
from rest_framework import test, status
from django.urls import reverse
from authors.apps.authentication.models import User


class TestArticlePagination(TestCase):
    def setUp(self):
        self.client = test.APIClient()
        self.user = User.objects.create_user(
            email='test@mail.com',
            username='Test',
            password='test1234'
        )

        # verify email
        test_user = User.objects.get(username='Test')
        test_user.is_verified = True
        test_user.save()
        self.login = self.client.post(
            reverse('authentication:user-login'),
            data={
                "user": {
                    "email": "test@mail.com",
                    "password": "test1234"
                }
            },
            format="json"
        )

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login.data['token'])

        for a in range(21):
            self.client.post(

                reverse('articles:create-list'),
                data={
                    "article": {
                        "title": "Test title",
                        "body": "This is a very awesome article on testing "
                                "tests",
                        "description": "Written by testing tester",
                        "tags": ["religion", "nature", "film"]
                    }
                },
                format="json"
            )

    def test_page_contains_ten_articles(self):
        response1 = self.client.get(
            "/api/articles/?page=1", format="json"
            )
        response2 = self.client.get(
            "/api/articles/?page=2", format="json"
            )
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response1.data['articles']), 10)
        self.assertEqual(len(response2.data['articles']), 10)
