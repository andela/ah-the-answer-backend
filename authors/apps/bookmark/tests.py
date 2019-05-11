from django.test import TestCase
from django.test import Client
from django.urls import reverse

from rest_framework import test, status
from rest_framework.test import APIClient

from authors.apps.articles.models import Article
from authors.apps.bookmark.models import Bookmark
from authors.apps.authentication.models import User


class TestCreateBookmark(TestCase):
    """Test suite that evaluates the outputs of the view that creates
    bookmarks under various conditions. """
    def setUp(self):
        """Create, authenticate and login a first user."""
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

        """Create, authenticate and login a second user."""
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
             "tags": [],
             "is_published": True
            }
        }
        article_response = self.client_1.post(reverse('articles:create-list'),
                                              self.user_article_1,
                                              format="json")
        self.id_1 = article_response.data['article']['id']

    def test_user_creates_bookmark(self):
        """Test if the 'create bookmark' view is able to successfully
        create a new article bookmark."""
        response = self.client_1.post(reverse('bookmark:bookmark-create',
                                      args=[self.id_1]), format='json')
        self.assertEqual(response.data['success'],
                         "Bookmark for article 'Titles Are For Turtles'"
                         "created.")

    def test_another_user_creates_bookmark(self):
        """Test if a two users can create the same bookmark."""
        self.client_1.post(reverse('bookmark:bookmark-create',
                                   args=[self.id_1]), format='json')
        self.token_2 = self.login_2.data['token']
        self.client_2.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token_2)
        response = self.client_2.post(reverse('bookmark:bookmark-create',
                                      args=[self.id_1]), format='json')
        self.assertEqual(response.data['success'],
                         "Bookmark for article 'Titles Are For Turtles'"
                         "created.")

    def test_user_attempts_to_repeat_a_bookmark(self):
        """Test if a user is able to create the same bookmark twice."""
        self.client_1.post(reverse('bookmark:bookmark-create',
                           args=[self.id_1]), format='json')
        response = self.client_1.post(reverse('bookmark:bookmark-create',
                                      args=[self.id_1]), format='json')
        self.assertEqual(response.data['error'],
                         "Article bookmark for this user already exists.")

    def test_user_attempts_to_bookmark_nonexistent_article(self):
        """Test if a user can create a bookmark for a nonexistent article."""
        false_id = 999
        response = self.client_1.post(reverse('bookmark:bookmark-create',
                                      args=[false_id]), format='json')
        self.assertEqual(response.data['error'], "No article with "
                                                 "that id found.")


class TestRetrieveBookmarks(TestCase):
    """Tests suite that evaluates the outputs of
    the view that retrieves user bookmarks."""
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
             "tags": [],
             "is_published": True
            }
        }
        self.user_article_2 = {
            "article":
            {
             "title": "Babies And Bananas",
             "body": "Baby Tings.",
             "description": "Describes Babies.",
             "tags": [],
             "is_published": True
            }
        }
        self.user_article_3 = {
            "article":
            {
             "title": "Tigers And Tamarinds.",
             "body": "Fancy Tigers Are Fancy.",
             "description": "Tiger Stuff.",
             "tags": [],
             "is_published": True
            }
        }
        response_1 = self.client_1.post(reverse('articles:create-list'),
                                        self.user_article_1, format="json")
        response_2 = self.client_1.post(reverse('articles:create-list'),
                                        self.user_article_2, format="json")
        response_3 = self.client_1.post(reverse('articles:create-list'),
                                        self.user_article_3, format="json")
        self.id_1 = response_1.data['article']['id']
        self.id_2 = response_2.data['article']['id']
        self.id_3 = response_3.data['article']['id']

    def test_user_fetches_bookmarks(self):
        """Test if a user can create several articles
        and bookmarks then fetch their bookmarks."""
        title_1 = "Titles Are For Turtles"
        title_2 = "Babies And Bananas"
        title_3 = "Tigers And Tamarinds."
        self.client_1.post(reverse('bookmark:bookmark-create',
                                   args=[self.id_1]), format='json')
        self.client_1.post(reverse('bookmark:bookmark-create',
                                   args=[self.id_2]), format='json')
        self.client_1.post(reverse('bookmark:bookmark-create',
                                   args=[self.id_3]), format='json')
        response = self.client_1.get(reverse('bookmark:bookmark-list'),
                                     format="json")
        self.assertEqual(len(response.data['success']), 3)
        self.assertEqual(response.data['success'][0], title_1)
        self.assertEqual(response.data['success'][1], title_2)
        self.assertEqual(response.data['success'][2], title_3)

    def test_attempt_to_fetch_empty_bookmarks(self):
        """Test if a user can fetch their empty bookmark list."""
        response = self.client_1.get(reverse('bookmark:bookmark-list'),
                                     format="json")
        self.assertEqual(len(response.data['success']), 0)
    
    def test_bookmark_object_readable_name(self):
        self.client_1.post(reverse('bookmark:bookmark-create',
                                   args=[self.id_1]), format='json')
        bookmark = Bookmark.objects.get(article_title="Titles Are For Turtles")
        self.assertEqual(bookmark.__str__(), "Titles Are For Turtles")


class TestRetrieveArticle(TestCase):

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
        self.user_article = {
            "article":
            {
             "title": "Titles Are For Turtles",
             "body": "Turtle shells galore.",
             "description": "Describes Turtles.",
             "tags": [],
             "is_published": True
            }
        }
        self.user_article_update = {
            "article":
            {
             "title": "Edit Title",
             "body": "Edited Body.",
             "description": "Edited Description",
             "tags": [],
             "is_published": True
            }
        }
        article_response = self.client_1.post(reverse('articles:create-list'),
                                              self.user_article_update,
                                              format="json")
        self.id_1 = article_response.data['article']['id']

    def test_retrieve_article_from_bookmark(self):
        title = "Titles Are For Turtles"
        self.client_1.post(reverse('bookmark:bookmark-create',
                           args=[self.id_1]), format='json')
        response = self.client_1.get(reverse('bookmark:bookmark-create',
                                     args=[self.id_1]), format='json')
        self.assertEqual(response.data['success'][0]['id'], self.id_1)

    def test_user_fetches_nonexistent_bookmark(self):
        title = "Titles Are For Turtles"
        response = self.client_1.get(reverse('bookmark:bookmark-create',
                                     args=[self.id_1]), format='json')
        self.assertEqual(response.data['error'], "No bookmark for "
                                                 "that article found.")
