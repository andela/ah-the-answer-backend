from django.test import TestCase
from django.urls import reverse
from rest_framework import test, status
from .models import Article


class TestArticle(TestCase):
    def setUp(self):
        self.client = test.APIClient()
        self.user_create = self.client.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "tester@mail.com",
                    "username": "tester",
                    "password": "tester1234"
                }
            },
            format="json"
        )
        self.user_create_2 = self.client.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "tester1@mail.com",
                    "username": "tester1",
                    "password": "tester1234"
                }
            },
            format="json"
        )
        self.user = self.client.post(
            reverse('authentication:user-login'),
            data={
                "user": {
                    "email": "tester@mail.com",
                    "password": "tester1234"
                }
            },
            format="json"
        )

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.user.data['token'])

    # CREATE TESTS

    def test_article_create(self):
        response = self.client.post(
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

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_missing_fields(self):
        response = self.client.post(
            reverse('articles:create-list'),
            data={
                "article": {
                    "title": "Test title",
                }
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data['errors'])
        self.assertTrue(response.data['errors']['body'])
        self.assertTrue(response.data['errors']['description'])

    def test_create_with_invalid_fields(self):
        response = self.client.post(
            reverse('articles:create-list'),
            data={
                "article": {
                    "title": "",
                    "body": "Hello world",
                    "description": "hello"
                }
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data['errors']['title'])

    # END OF CREATE TESTS

    # RETRIEVE TESTS

    def test_get_without_token(self):
        self.client.logout()

        response = self.client.get(
            reverse(
                'articles:create-list',
            ),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_article(self):
        response = self.client.get(
            reverse(
                'articles:create-list',
            ),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_specific_article(self):
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
        response = self.client.get(
            reverse(
                'articles:details',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # test content as well as status code

    def test_get_specific_non_existent(self):
        response = self.client.get(
            reverse(
                'articles:details',
                kwargs={
                    "slug": "test-article-one"
                }
            ),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # END OF RETRIEVE TESTS

    # UPDATE TESTS

    def test_update_article(self):
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
        response = self.client.put(
            reverse(
                'articles:details',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            data={
                "article": {
                    "title": "Test title updated",
                    "description": "Written by updater",
                }
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test content as well as status code

    def test_update_non_existent(self):
        response = self.client.put(
            reverse(
                'articles:details',
                kwargs={
                    "slug": "test-article-one"
                }
            ),
            data={
                "article": {
                    "title": "Test title updated",
                    "description": "Written by updater",
                }
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_not_authenticated(self):

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
        self.client.logout()
        response = self.client.put(
            reverse(
                'articles:details',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            data={
                "article": {
                    "title": "Test title updated",
                    "description": "Written by updater",
                }
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_not_authorized(self):
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
        self.client.logout()
        self.client.login(username='tester1', password='tester1234')
        response = self.client.put(
            reverse(
                'articles:details',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            data={
                "article": {
                    "title": "Test title updated",
                    "description": "Written by updater",
                }
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # END OF UPDATE TESTS

    # DELETE TESTS
    def test_delete_article(self):
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
        response = self.client.delete(
            reverse(
                'articles:details',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_non_existent(self):
        response = self.client.delete(
            reverse(
                'articles:details',
                kwargs={
                    "slug": "test-article-one"
                }
            ),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_not_authorized(self):
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
        self.client.logout()
        self.client.login(username='tester1', password='tester1234')
        response = self.client.delete(
            reverse(
                'articles:details',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # END OF DELETE TESTS

    def tearDown(self):
        Article.objects.all().delete()
