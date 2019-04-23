from django.test import TestCase
from authors.apps.authentication.models import User
from django.urls import reverse
from rest_framework import test, status
from authors.apps.articles.models import Article


class TestArticle(TestCase):
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

        # Create an article
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login.data['token'])

        self.client.post(
            reverse('articles:create-list'),
            data={
                "article": {
                    "title": "Test title",
                    "body": "This is a very awesome article on testing tests",
                    "description": "Written by testing tester",
                    "tags": []
                }
            },
            format="json"
        )

    def test_facebook_share(self):
        article_response = self.client.get(
            reverse(
                'articles:details',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            format="json"
        )
        response = self.client.get(
            reverse('articles:share-article', kwargs={
                    'slug': article_response.data['article']['slug'],
                    'provider': 'facebook'}),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['share']['provider'], 'facebook')
        self.assertTrue(response.data['share']['link'])

    def test_twitter_share(self):
        article_response = self.client.get(
            reverse(
                'articles:details',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            format="json"
        )
        response = self.client.get(
            reverse('articles:share-article', kwargs={
                    'slug': article_response.data['article']['slug'],
                    'provider': 'twitter'}),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['share']['provider'], 'twitter')
        self.assertTrue(response.data['share']['link'])

    def test_reddit_share(self):
        article_response = self.client.get(
            reverse(
                'articles:details',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            format="json"
        )
        response = self.client.get(
            reverse('articles:share-article', kwargs={
                    'slug': article_response.data['article']['slug'],
                    'provider': 'reddit'}),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['share']['provider'], 'reddit')
        self.assertTrue(response.data['share']['link'])

    def test_telegram_share(self):
        article_response = self.client.get(
            reverse(
                'articles:details',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            format="json"
        )
        response = self.client.get(
            reverse('articles:share-article', kwargs={
                    'slug': article_response.data['article']['slug'],
                    'provider': 'telegram'}),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['share']['provider'], 'telegram')
        self.assertTrue(response.data['share']['link'])

    def test_linkedin_share(self):
        article_response = self.client.get(
            reverse(
                'articles:details',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            format="json"
        )
        response = self.client.get(
            reverse('articles:share-article', kwargs={
                    'slug': article_response.data['article']['slug'],
                    'provider': 'linkedin'}),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['share']['provider'], 'linkedin')
        self.assertTrue(response.data['share']['link'])

    def test_mail_share(self):
        article_response = self.client.get(
            reverse(
                'articles:details',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            format="json"
        )
        response = self.client.get(
            reverse('articles:share-article', kwargs={
                    'slug': article_response.data['article']['slug'],
                    'provider': 'email'}),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['share']['provider'], 'email')
        self.assertTrue(response.data['share']['link'])

    def test_invalid_provider(self):
        article_response = self.client.get(
            reverse(
                'articles:details',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            format="json"
        )
        response = self.client.get(
            reverse('articles:share-article', kwargs={
                    'slug': article_response.data['article']['slug'],
                    'provider': 'facebok'}),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'],
                         'Please select a valid provider - '
                         'twitter, facebook, email, telegram, '
                         'linkedin, reddit')

    def tearDown(self):
        Article.objects.all().delete()
