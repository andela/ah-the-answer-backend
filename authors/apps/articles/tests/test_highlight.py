from django.test import TestCase
from authors.apps.authentication.models import User
from django.urls import reverse
from rest_framework import test, status
from authors.apps.articles.models import Article, Highlight
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

    def test_highlighting(self):
        response = self.client.post(
            reverse(
                'articles:highlight-article',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            data={
                "highlight": {
                    "start": 0,
                    "end": 10
                }
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Highlight has been added')
        self.assertEqual(response.data['highlight']['start'], 0)
        self.assertEqual(response.data['highlight']['end'], 10)
        self.assertEqual(response.data['highlight']['section'], 'This is a v')

    def test_highlighting_nonexistent_article(self):
        response = self.client.post(
            reverse(
                'articles:highlight-article',
                kwargs={
                    "slug": "test-article-one-two"
                }
            ),
            data={
                "highlight": {
                    "start": 0,
                    "end": 10
                }
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'],
                         'The article requested does not exist')

    def test_unhighlighting(self):
        article = Article.objects.all().first()
        self.client.post(
            reverse(
                'articles:highlight-article',
                kwargs={
                    "slug": article.slug
                }
            ),
            data={
                "highlight": {
                    "start": 0,
                    "end": 11
                }
            },
            format="json"
        )
        response = self.client.post(
            reverse(
                'articles:highlight-article',
                kwargs={
                    "slug": article.slug
                }
            ),
            data={
                "highlight": {
                    "start": 0,
                    "end": 11
                }
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'],
                         'Highlight has been removed')

    def test_highlighting_with_comment(self):
        response = self.client.post(
            reverse(
                'articles:highlight-article',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            data={
                "highlight": {
                    "start": 0,
                    "end": 10,
                    "comment": "Nice piece"
                }
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Comment has been added')
        self.assertEqual(response.data['highlight']['start'], 0)
        self.assertEqual(response.data['highlight']['end'], 10)
        self.assertEqual(response.data['highlight']['section'], 'This is a v')
        self.assertEqual(response.data['highlight']['comment'], 'Nice piece')

    def test_uncomment_highlight(self):
        self.client.post(
            reverse(
                'articles:highlight-article',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            data={
                "highlight": {
                    "start": 0,
                    "end": 11,
                    "comment": "Nice piece"
                }
            },
            format="json"
        )
        response = self.client.post(
            reverse(
                'articles:highlight-article',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            data={
                "highlight": {
                    "start": 0,
                    "end": 11,
                    "comment": "Nice piece"
                }
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Comment has been removed')

    def test_highlighting_start_equals_end(self):
        response = self.client.post(
            reverse(
                'articles:highlight-article',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            data={
                "highlight": {
                    "start": 10,
                    "end": 10
                }
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['message'],
            'Start position cannot be equal to or greater than end position')

    def test_highlighting_start_greater_than_end(self):
        response = self.client.post(
            reverse(
                'articles:highlight-article',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            data={
                "highlight": {
                    "start": 15,
                    "end": 10
                }
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['message'],
            'Start position cannot be equal to or greater than end position')

    def test_highlighting_end_out_of_range(self):
        response = self.client.post(
            reverse(
                'articles:highlight-article',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            data={
                "highlight": {
                    "start": 15,
                    "end": 1000
                }
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['message'],
            'End position is greater than the article size of 46')

    def test_get_all_highlights(self):
        response = self.client.post(
            reverse(
                'articles:highlight-article',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            data={
                "highlight": {
                    "start": 15,
                    "end": 1000
                }
            },
            format="json"
        )
        response = self.client.get(
            reverse(
                'articles:highlight-article',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['highlights'], [])

    def test_update_highlighted_article(self):

        self.client.post(
            reverse(
                'articles:highlight-article',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            data={
                "highlight": {
                    "start": 0,
                    "end": 10
                }
            },
            format="json"
        )

        self.client.put(
            reverse(
                'articles:details',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            data={
                "article": {
                    "body": "1This is a very awesome article on testing tests"
                }
            },
            format="json"
        )

        response = self.client.get(
            reverse(
                'articles:highlight-article',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['highlights'][0]['start'], 1)
        self.assertEqual(response.data['highlights'][0]['end'], 11)
        self.assertEqual(response.data['highlights'][0]['section'],
                         'This is a v')

    def test_update_article_removing_highlighted_section(self):
        """Test to check if the highlight is deleted when
        article is updated and that block is removed in the article body"""
        self.client.post(
            reverse(
                'articles:highlight-article',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            data={
                "highlight": {
                    "start": 0,
                    "end": 10
                }
            },
            format="json"
        )

        self.client.put(
            reverse(
                'articles:details',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            data={
                "article": {
                    "body": "This is a great article on testing tests"
                }
            },
            format="json"
        )

        response = self.client.get(
            reverse(
                'articles:highlight-article',
                kwargs={
                    "slug": Article.objects.get().slug
                }
            ),
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['highlights'], [])

    def tearDown(self):
        Article.objects.all().delete()
