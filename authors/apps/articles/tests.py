from django.test import TestCase
from django.urls import reverse
from rest_framework import test, status
# from .models import Article


# Create your tests here.
class TestArticle(TestCase):
    def setUp(self):
        pass
    #     self.client = test.APIClient()
    #     self.user_create = self.client.post(
    #         reverse('authentication:user-signup'),
    #         data={
    #             "user": {
    #                 "email": "tester@mail.com",
    #                 "username": "tester",
    #                 "password": "tester1234"
    #             }
    #         },
    #         format="json"
    #     )
    #     self.user = self.client.post(
    #         reverse('authentication:user-login'),
    #         data={
    #             "user": {
    #                 "email": "tester@mail.com",
    #                 "password": "tester1234"
    #             }
    #         },
    #         format="json"
    #     )
    #     self.client.credentials(HTTP_AUTHORIZATION='Bearer' + self.user.token)
    #     self.article = Article.objects.create(
    #         title="Test title",
    #         body="This is a very awesome article on testing tests",
    #         description="Written by testing tester"
    #     )

    # # CREATE TESTS

    # def test_article_create(self):
    #     response = self.client.post(
    #         reverse('articles:create'),
    #         data={
    #             "title": "Test title",
    #             "body": "This is a very awesome article on testing tests",
    #             "description": "Written by testing tester",
    #         },
    #         format="json"
    #     )

    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_missing_fields(self):
        pass
        # response = self.client.post(
        #     reverse('articles:create'),
        #     data={
        #         "title": "Test title",
        #     },
        #     format="json"
        # )

        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # self.assertTrue(response.data['errors'])
        # self.assertTrue(response.data['errors']['body'])
        # self.assertTrue(response.data['errors']['description'])

    def test_create_with_invalid_fields(self):
        pass

    # END OF CREATE TESTS

    # RETRIEVE TESTS

    def test_get_without_token(self):
        pass

    def test_get_all_article(self):
        pass
        # response = self.client.get(
        #     reverse(
        #         'articles:list',
        #     ),
        #     format="json"
        # )

        # self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_specific_article(self):
        pass
        # response = self.client.get(
        #     reverse(
        #         'articles:details',
        #         kwargs={
        #             "id": self.article.id
        #         }
        #     ),
        #     format="json"
        # )

        # self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_specific_non_existent(self):
        pass

    # END OF RETRIEVE TESTS

    # UPDATE TESTS

    def test_update_article(self):
        pass
        # response = self.client.put(
        #     reverse(
        #         'articles:details',
        #         kwargs={
        #             "id": self.article.id
        #         }
        #     ),
        #     data={
        #         "title": "Test title updated",
        #         "description": "Written by updater",
        #     },
        #     format="json"
        # )

        # self.assertEqual(response.status_code, status.HTTP_200_OK)

        # self.assertNotEqual(self.article.title, 'Test title')
        # self.assertNotEqual(
        #     self.article.description,
        #     'Written by testing tester'
        # )

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
        # response = self.client.delete(
        #     reverse(
        #         'articles:details',
        #         kwargs={
        #             "id": self.article.id
        #         }
        #     ),
        #     format="json"
        # )

        # self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_non_existent(self):
        pass

    def test_delete_not_authorized(self):
        pass

    # END OF DELETE TESTS

    def tearDown(self):
        pass
        # Article.objects.get(id=self.article.id).delete()
