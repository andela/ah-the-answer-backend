from django.test import TestCase
from django.urls import reverse
from rest_framework import test, status
from authors.apps.authentication.models import User
from authors.apps.articles.models import Article, LikeArticles
from authors.apps.articles.serializers import LikeArticleSerializer
from django.db.models import Count


class TestStats(TestCase):
    def setUp(self):
        self.client = test.APIClient()
        self.user = User.objects.create_user(
            username='test', email="test@mail.com", password='test1234')
        self.user.is_verified = True
        self.user.save()
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
        self.token = self.login.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)

    # User/ Personal statistics
    def test_can_get_articles_authored(self):
        """
        Retrieves all the articles that a user has authored
        """

        # Create an article
        article_create = self.client.post(
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

        articles = Article.objects.filter(author=self.user)

        self.assertEqual(article_create.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(articles), 1)

    def test_can_get_articles_authored(self):
        """
        Retrieves all the articles that a user has authored
        """
        res_before = self.client.get(
            reverse(
                'stats:user-articles',
                kwargs={"username": self.user.username}
            )
        )

        article_create = self.client.post(
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

        res_after = self.client.get(
            reverse(
                'stats:user-articles',
                kwargs={"username": self.user.username}
            )
        )

        self.assertEqual(res_after.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res_after.data['articles_count'],
            res_before.data['articles_count'] + 1
        )

    def test_can_get_count_of_liked_articles(self):
        """Checks that a user can retrieve a count of all the articles
            that they have liked"""

        liked = LikeArticles.objects.filter(user=self.user).count()

        res = self.client.get(
            reverse(
                'stats:liked-articles',
                kwargs={"username": self.user.username}
            )
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['likes'], liked)

    # Global level
    def test_can_get_most_liked_articles(self):

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
        article1 = Article.objects.all()[0]
        article2 = Article.objects.all()[1]
        self.client.post(
            reverse(
                'articles:like-article',
                kwargs={
                    "slug": article1.slug
                }
            ))
        self.client.post(
            reverse(
                'articles:like-article',
                kwargs={
                    "slug": article2.slug
                }
            ))
        res = self.client.get(reverse('stats:popular-articles'))
        top = LikeArticles.objects.filter(likes__gt=0).order_by('-likes')\
            .values('article').annotate(total_likes=Count('likes'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data['popular'],
            LikeArticleSerializer(top, many=True).data
        )
