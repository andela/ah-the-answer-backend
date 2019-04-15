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
        """Create, authenticate and log in a user."""
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
             "title": "Titles Are For Turtles.",
             "body": "Turtle shells galore.",
             "description": "Describes Turtles.",
             "is_published": True
            }
        }

    def test_user_creates_bookmark(self):
        """Test if the 'create bookmark' view is able to successfully
        create a new article bookmark."""
        title = 'Titles Are For Turtles'
        self.client.post(reverse('articles:create-list'),
                         self.user_article_1, format="json")
        response = client.post(reverse('bookmark:bookmark-create'), args=title,
                               format='json')
        self.assertEqual(response.data['success'],
                         "Bookmark for article 'Titles Are For Turtles' "
                         "created.")
    
    def test_user_attempts_to_repeat_a_bookmark(self):
        """Test if a user is able to create a bookmark."""
        title = 'Titles Are For Turtles'
        self.client.post(reverse('articles:create-list'),
                         self.user_article_1, format="json")
        self.client.post(reverse('bookmark:bookmark-create'), args=title,
                         format='json')
        response = client.post(reverse('bookmark:bookmark-create'), args=title,
                               format='json')
        self.assertEqual(response.data['error'],
                         "You already have a bookmark for this "
                         "article.")
    
    def test_user_attempts_to_bookmark_nonexistent_article(self):
        """Test if the 'create bookmark' view is able to successfully
        create a new article bookmark."""
        title = 'Quantum Physics For Dummies'
        self.client.post(reverse('articles:create-list'),
                         self.user_article_1, format="json")
        response = client.post(reverse('bookmark:bookmark-create'), args=title,
                               format='json')
        self.assertEqual(response.data['error'], "No article with that title found.")