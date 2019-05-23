import tempfile

from django.test import TestCase
from authors.apps.authentication.models import User
from django.urls import reverse
from PIL import Image
from rest_framework import test, status
from authors.apps.articles.models import Article, ArticleImage
from authors.apps.articles.filters import ArticleFilter


class TestArticle(TestCase):
    def setUp(self):
        self.client = test.APIClient()
        self.user = User.objects.create_user(
            email='test@mail.com',
            username='Test',
            password='test1234'
        )

        # verify email
        self.test_user = User.objects.get(username='Test')
        self.test_user.is_verified = True
        self.test_user.save()
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

    def test_article_model(self):
        """Test that the article model is created successfully"""
        article = Article.objects.create(
            title="Test Title Here",
            body="A nice article",
            description="Description is also good",
            author=self.test_user
        )
        self.assertTrue(article)
        self.assertEqual(article.body, 'A nice article')
        self.assertEqual(article.__str__(), 'Test Title Here')

    # CREATE TESTS

    def test_article_create(self):
        response = self.client.post(
            reverse('articles:create-list'),
            data={
                "article": {
                    "title": "Test title",
                    "body": "This is a very awesome article on testing tests",
                    "description": "Written by testing tester",
                    "tags": ["religion", "nature", "film"]
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

    def test_create_with_invalid_tags_field(self):
        response = self.client.post(
            reverse('articles:create-list'),
            data={
                "article": {
                    "title": "the house in the hill",
                    "body": "the hill was grassy with a single house apex",
                    "description": "a hill story",
                    "tags": "0"
                }
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data['errors']['tags'])

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
                    "tags": ["religion", "nature", "film"]
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
                    "tags": ["religion", "nature", "film"]
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
                    "tags": ["study", "cosmos", "physics"]
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
                    "tags": ["religion", "nature", "film"]
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
                    "tags": ["religion", "nature", "film"]
                }
            },
            format="json"
        )

        self.client_2 = test.APIClient()
        self.user_2 = User.objects.create_user(
            username='Test2',
            email='test2@mail.com',
            password='test1234',
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
                    "tags": ["religion", "nature", "film"]
                }
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data['message'],
            'Only the owner can edit this article.'
        )

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
                    "tags": ["religion", "nature", "film"]
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
                    "tags": ["religion", "nature", "film"]
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
                    "tags": ["religion", "nature", "film"]
                }
            },
            format="json"
        )

        self.client_3 = test.APIClient()
        self.user = User.objects.create_user(
            email='test3@mail.com',
            username='Test3',
            password='test1234'
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
        self.assertEqual(
            response.data['message'],
            'Only the owner can delete this article.'
        )

    # END OF DELETE TESTS
    @property
    def temporary_image(self):
        """
        Creates a dummy, temporary image for testing purposes
        Returns a new temporary image file
        """

        image = Image.new('RGB', (1, 1))
        tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(tmp_file, 'jpeg')
        # important because after save(),
        # the fp is already at the end of the file
        tmp_file.seek(0)  # retrieves the created temp file
        return tmp_file

    def test_image_upload_successful(self):
        """
        This test case tests that an authenticated
        user can upload image for their article
        """
        self.client.post(
            reverse('articles:create-list'),
            data={
                "article": {
                    "title": "Test title",
                    "body": "This is a very awesome article on testing tests",
                    "description": "Written by testing tester",
                    "tags": ["religion", "nature", "film"]
                }
            },
            format="json"
        )
        res = self.client.post(
            reverse('articles:add-image',
                    kwargs={
                        "slug": Article.objects.get().slug
                    }),
            data={
                "file": self.temporary_image
            },
            format='multipart'
        )
        self.client.delete(
            reverse(
                'articles:image-details',
                kwargs={
                    "slug": Article.objects.get().slug,
                    "id": ArticleImage.objects.get().id,
                }
            ),
            format="json"
        )
        self.assertEquals(res.status_code, status.HTTP_200_OK)

    def test_invalid_image_upload(self):
        """
        This test case tests that an authenticated
        user can't upload invalid image for their article
        """
        self.client.post(
            reverse('articles:create-list'),
            data={
                "article": {
                    "title": "Test title",
                    "body": "This is a very awesome article on testing tests",
                    "description": "Written by testing tester",
                    "tags": ["religion", "nature", "film"]
                }
            },
            format="json"
        )
        res = self.client.post(
            reverse('articles:add-image',
                    kwargs={
                        "slug": Article.objects.get().slug
                    }),
            data={
                "file": "self.temporary_image"
            },
            format='multipart'
        )
        self.assertEquals(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertRaises(Exception)

    def test_user_can_search_articles(self):
        response = self.client.get(
            "/api/articles/?search=raywire",
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_search_articles_by_tags(self):
        response = self.client.get(
            "/api/articles/?search=religion,nature",
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_filter_articles_by_title(self):
        self.client.post(
            reverse('articles:create-list'),
            data={
                "article": {
                    "title": "Test title",
                    "body": "This is a very awesome article on testing tests",
                    "description": "Written by testing tester",
                    "tags": ["religion", "nature", "film"]
                }
            },
            format="json"
        )
        response = self.client.get(
            "/api/articles/?title=Test title",
            format="json"
        )
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
                    "tags": ["religion", "nature", "film"]
                }
            },
            format="json"
        )
        response = self.client.get("/api/articles/?author=Test", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['articles'])

    def tearDown(self):
        Article.objects.all().delete()
