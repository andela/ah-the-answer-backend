from django.test import TestCase
from authors.apps.authentication.models import User
from django.urls import reverse
from rest_framework import test, status
from authors.apps.articles.models import FavoriteModel

class FavoriteTestCase(TestCase):
    def test_user_can_create_a_favorite(self):
        pass
    def test_user_cant_favorite_an_invalid_article(self):
        pass
    def test_user_can_remove_from_favorite(self):
        pass
    def test_user_get_all_favourites(self):
        pass