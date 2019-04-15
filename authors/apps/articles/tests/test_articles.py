from django.test import TestCase
from authors.apps.authentication.models import User
from django.urls import reverse
from rest_framework import test, status
from authors.apps.articles.models import Article
from authors.apps.articles.filters import ArticleFilter


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

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login.data['token'])

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
        self.assertTrue(response.data['success'])
        self.assertTrue(response.data['article'])

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
        self.assertTrue(response.data['success'])
        self.assertTrue(response.data['article'])

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

        self.client_2 = test.APIClient()
        self.user_2 = self.client_2.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "test2@mail.com",
                    "username": "Test2",
                    "password": "test1234"
                }
            },
            format="json"
        )

        test_user_2 = User.objects.get(username='Test2')
        test_user_2.is_verified = True
        test_user_2.save()
        self.login_2 = self.client_2.post(
            reverse('authentication:user-login'),
            data={
                "user": {
                    "email": "test2@mail.com",
                    "password": "test1234"
                }
            },
            format="json"
        )

        self.client_2.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_2.data['token'])      
        response = self.client_2.put(
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
        self.assertEqual(response.data['message'], 'Only the owner can edit this article.')

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

    def test_delete_not_authenticated(self):
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

        self.client_3 = test.APIClient()
        self.user_3 = self.client_3.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "test3@mail.com",
                    "username": "Test3",
                    "password": "test1234"
                }
            },
            format="json"
        )

        test_user_3 = User.objects.get(username='Test3')
        test_user_3.is_verified = True
        test_user_3.save()
        self.login_3 = self.client_3.post(
            reverse('authentication:user-login'),
            data={
                "user": {
                    "email": "test3@mail.com",
                    "password": "test1234"
                }
            },
            format="json"
        )

        self.client_3.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login_3.data['token'])

        response = self.client_3.delete(
            reverse(
                'articles:details',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['message'], 'Only the owner can delete this article.')

    # END OF DELETE TESTS

    def test_user_can_search_articles(self):
        response = self.client.get("/api/articles/?search=raywire", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_filter_articles_by_title(self):
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
        response = self.client.get("/api/articles/?title=Test title", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['articles'])

    def test_user_can_filter_articles_by_author(self):
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
        response = self.client.get("/api/articles/?author=Test", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['articles'])

    def tearDown(self):
        Article.objects.all().delete()
