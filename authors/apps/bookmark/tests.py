from django.test import TestCase
from django.test import Client
from django.urls import reverse
from rest_framework import test, status
from rest_framework.test import APIClient

from authors.apps.articles.models import Article
from authors.apps.bookmark.models import Bookmark
from authors.apps.authentication.models import User


class TestCreateBookmark(TestCase):
    """Tests the whether a whether a user can create a new bookmark """

    def setUp(self):
        """Create, authenticate and log a first user."""
        self.client_1 = APIClient()
        self.user_1 = self.client_1.post(
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
        test_user_1 = User.objects.get(username='Bob')
        test_user_1.is_verified = True
        test_user_1.save()
        self.login_1 = self.client_1.post(
            reverse('authentication:user-login'),
            data={
                "user": {
                    "email": "demo@mail.com",
                    "password": "Bob12345"
                }
            },
            format="json"
        )
        self.token_1 = self.login_1.data['token']
        self.client_1.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_1)

        """Create, authenticate and log a second user."""
        self.client_2 = APIClient()
        self.user_2 = self.client_2.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "mail@demo.com",
                    "username": "Mary",
                    "password": "abc123ok"
                }
            },
            format="json"
        )
        test_user_2 = User.objects.get(username='Mary')
        test_user_2.is_verified = True
        test_user_2.save()
        self.login_2 = self.client_2.post(
            reverse('authentication:user-login'),
            data={
                "user": {
                    "email": "mail@demo.com",
                    "password": "abc123ok"
                }
            },
            format="json"
        )
        self.user_article_1 = {
            "article":
            {
             "title": "Titles Are For Turtles",
             "body": "Turtle shells galore.",
             "description": "Describes Turtles.",
             "is_published": True
            }
        }

    def test_user_creates_bookmark(self):
        """Test if the 'create bookmark' view is able to successfully
        create a new article bookmark."""
        title = 'Titles Are For Turtles'
        self.client_1.post(reverse('articles:create-list'),
                           self.user_article_1, format="json")
        response = self.client_1.post(reverse('bookmark:bookmark-create',
                                      args=[title]), format='json')
        self.assertEqual(response.data['success'],
                         "Bookmark for article 'Titles Are For Turtles'"
                         "created.")

    def test_another_user_creates_bookmark(self):
        """Test if a two users can create the same bookmark."""
        title = 'Titles Are For Turtles'
        self.client_1.post(reverse('articles:create-list'),
                           self.user_article_1, format="json")
        self.client_1.post(reverse('bookmark:bookmark-create',
                                   args=[title]), format='json')
        self.token_2 = self.login_2.data['token']
        self.client_2.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_2)
        response = self.client_2.post(reverse('bookmark:bookmark-create',
                                      args=[title]), format='json')
        self.assertEqual(response.data['success'],
                         "Bookmark for article 'Titles Are For Turtles'"
                         "created.")
        
    def test_user_attempts_to_repeat_a_bookmark(self):
        """Test if a user is able to create the same bookmark twice."""
        title = 'Titles Are For Turtles'
        self.client_1.post(reverse('articles:create-list'),
                           self.user_article_1, format="json")
        self.client_1.post(reverse('bookmark:bookmark-create', args=[title]),
                           format='json')
        response = self.client_1.post(reverse('bookmark:bookmark-create',
                                      args=[title]), format='json')
        self.assertEqual(response.data['error'],
                         "Article bookmark for this user already exists.")

    def test_user_attempts_to_bookmark_nonexistent_article(self):
        """Test if a user can create a bookmark for a nonexistent article."""
        title = 'Quantum Physics For Dummies'
        self.client_1.post(reverse('articles:create-list'),
                           self.user_article_1, format="json")
        response = self.client_1.post(reverse('bookmark:bookmark-create',
                                      args=[title]), format='json')
        self.assertEqual(response.data['error'], "No article with that title found.")


class TestRetrieveBookmarks(TestCase):
    """Tests related to users fetching a bookmark."""

    def setUp(self):
        self.client_1 = APIClient()
        self.user_1 = self.client_1.post(
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
        test_user_1 = User.objects.get(username='Bob')
        test_user_1.is_verified = True
        test_user_1.save()
        self.login_1 = self.client_1.post(
            reverse('authentication:user-login'),
            data={
                "user": {
                    "email": "demo@mail.com",
                    "password": "Bob12345"
                }
            },
            format="json"
        )
        self.token_1 = self.login_1.data['token']
        self.client_1.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_1)
        self.user_article_1 = {
            "article":
            {
             "title": "Titles Are For Turtles",
             "body": "Turtle shells galore.",
             "description": "Describes Turtles.",
             "is_published": True
            }
        }
        
    def test_user_fetches_bookmarks(self):
        self.client_1.post(reverse('articles:create-list'),
                           self.user_article_1, format="json")
        response = self.client_1.post(reverse('bookmark:bookmark-list'), format="json")
        self.assertEqual(response.data['error'], "No article with that title found.")


