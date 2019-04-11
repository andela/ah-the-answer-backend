from django.test import TestCase
from authors.apps.authentication.models import User
from django.urls import reverse
from rest_framework import test, status
from authors.apps.articles.models import FavoriteModel, Article


class FavoriteTestCase(TestCase):
    def setUp(self):
        self.client = test.APIClient()
        self.user = self.client.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "test@mail.com",
                    "username": "Test",
                    "password": "test1234"
                }
            },
            format="json"
        )

        # verify email
        test_user = User.objects.get(username='Test')
        test_user.is_verified = True
        test_user.save()

        # Get authorization token
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

    def test_user_can_favorite(self):
        self.client.post(
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
        res = self.client.post(
            reverse('articles:favorite',
                    kwargs={
                        "slug": Article.objects.get().slug
                    })
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['message'], "Added to favorites")

    def test_user_cant_favorite_an_invalid_article(self):
        res = self.client.post(
            reverse('articles:favorite',
                    kwargs={
                        'slug': 'dfadfa'
                    })
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        # self.assertEqual(res.data['message'],
        #                  "The article requested does not exist")

    def test_user_get_all_favorites(self):
        self.client.post(
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
        res = self.client.post(
            reverse('articles:favorite',
                    kwargs={
                        "slug": Article.objects.get().slug
                    }),
            format='json'
        )
        res = self.client.get(reverse('articles:favorite-list'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'],
                         FavoriteModel.objects.all().count())

    def test_user_can_remove_from_favorite(self):
        self.client.post(
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
        res = self.client.post(
            reverse('articles:favorite',
                    kwargs={
                        "slug": Article.objects.get().slug
                    }),
            format='json'
        )
        res = self.client.delete(
            reverse('articles:favorite',
                    kwargs={
                        "slug": Article.objects.get().slug
                    }),
                    format='json'
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['message'],
                         "Removed from favorites")
