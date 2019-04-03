from django.test import TestCase
from django.urls import reverse
from rest_framework import test, status


class TestArticle(TestCase):
    def setUp(self):
        pass

    # CREATE TESTS

    def test_article_create(self):
        pass

    def test_create_missing_fields(self):
        pass

    def test_create_with_invalid_fields(self):
        pass

    # END OF CREATE TESTS

    # RETRIEVE TESTS

    def test_get_without_token(self):
        pass

    def test_get_all_article(self):
        pass

    def test_get_specific_article(self):
        pass

    def test_get_specific_non_existent(self):
        pass

    # END OF RETRIEVE TESTS

    # UPDATE TESTS

    def test_update_article(self):
        pass

    def test_update_non_existent(self):
        pass

    def test_update_not_authenticated(self):
        pass

    def test_update_not_authorized(self):
        pass

    # END OF UPDATE TESTS

    # DELETE TESTS
    def test_delete_article(self):
        pass

    def test_delete_non_existent(self):
        pass

    def test_delete_not_authorized(self):
        pass

    # END OF DELETE TESTS

    def tearDown(self):
        pass
        # Article.objects.get(id=self.article.id).delete()
