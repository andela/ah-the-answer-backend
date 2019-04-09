from django.test import TestCase
from django.urls import reverse
from rest_framework import test, status
from rest_framework.test import APIClient
from authors.apps.articles.models import Article, ReviewsModel
from authors.apps.authentication.models import User


class TestReviewModel(TestCase):
    def setUp(self):
        user = User.objects.create(username="johndoe")
        article = Article.objects.create(
            title="Test title",
            body="This is a very awesome article on testing tests",
            description="Written by testing tester",
            author=user
        )
        self.review_body = "John Doe"
        self.rating_value = int(5)
        self.review = ReviewsModel(
            article=article,
            review_body=self.review_body,
            rating_value=self.rating_value,
            reviewed_by=user,
        )

    def test_model_can_create_review(self):
        """Test whether model can create a record"""
        initial = ReviewsModel.objects.count()
        self.review.save()
        updated = ReviewsModel.objects.count()
        self.assertNotEqual(initial, updated)


class ReviewTestCase(TestCase):
    def setUp(self):
        """
        This setup creates and logs in a new user. After login the user
        receives an auth token that is stored and will be used to access the
        protected views contained in this test series. Lastly, two mock profile
        sets for a user are made: the first being valid,
        the second being invalid.
        """
        self.client = APIClient()
        self.client2 = APIClient()
        self.user = self.client.post(
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
        self.user2 = self.client2.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "pete@mail.com",
                    "username": "Pete",
                    "password": "Pete12345"
                }
            },
            format="json"
        )
        test_user = User.objects.get(username="Bob")
        test_user.is_verified = True
        test_user.save()
        test_user2 = User.objects.get(username="Pete")
        test_user2.is_verified = True
        test_user2.save()
        self.login = self.client.post(
            reverse('authentication:user-login'),
            data={
                "user": {
                    "email": "demo@mail.com",
                    "password": "Bob12345"
                }
            },
            format="json"
        )
        self.login2 = self.client2.post(
            reverse('authentication:user-login'),
            data={
                "user": {
                    "email": "pete@mail.com",
                    "password": "Pete12345"
                }
            },
            format="json"
        )
        self.token = self.login.data['token']
        self.token2 = self.login2.data['token']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.client2.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token2)

    def test_user_can_create_review(self):
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
        response = self.client2.post(
            reverse('articles:review', kwargs={
                "slug": Article.objects.get().slug
            }),
            data={
                "review": {
                    "review_body": "I really liked the article",
                    "rating_value": 4
                }
            },
            format="json"
        )
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_can_get_reviews(self):
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
        response = self.client2.post(
            reverse('articles:review', kwargs={
                "slug": Article.objects.get().slug
            }),
            data={
                "review": {
                    "review_body": "I really liked the article",
                    "rating_value": 4
                }
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client2.get(
            reverse('articles:review', kwargs={
                "slug": Article.objects.get().slug
            }),
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, "I really liked the article")

    def test_user_can_edit_review(self):
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
        response = self.client2.post(
            reverse('articles:review', kwargs={
                "slug": Article.objects.get().slug
            }),
            data={
                "review": {
                    "review_body": "I really liked the article",
                    "rating_value": 4
                }
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client2.put(reverse('articles:review', kwargs={
            "slug": Article.objects.get().slug
        }), data={
            "review": {
                "review_body": "I did not liked the article",
                "rating_value": 3
            }
        },
            format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_can_delete_review(self):
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
        response = self.client2.post(
            reverse('articles:review', kwargs={
                "slug": Article.objects.get().slug
            }),
            data={
                "review": {
                    "review_body": "I really liked the article",
                    "rating_value": 4
                }
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client2.delete(reverse('articles:review', kwargs={
            "slug": Article.objects.get().slug
        }))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_delete = self.client2.get(
            reverse('articles:review', kwargs={
                "slug": Article.objects.get().slug
            }),
            format="json"
        )
        print(response_delete.data)
        self.assertEqual(response_delete.status_code,
                         status.HTTP_404_NOT_FOUND)
        self.assertRaises(Exception)

    def test_unautheticated_user_cant_create_review(self):
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
        self.client2.logout()
        response = self.client2.post(
            reverse('articles:review', kwargs={
                "slug": Article.objects.get().slug
            }),
            data={
                "review": {
                    "review_body": "I really liked the article",
                    "rating_value": 4
                }
            },
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    def test_review_creation_with_wrong_values(self):
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
        response = self.client2.post(
            reverse('articles:review', kwargs={
                "slug": Article.objects.get().slug
            }),
            data={
                "review": {
                    "review_body": "I really liked the article",
                    "rating_value": True
                }
            },
            format="json"
        )
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cannot_review_own_article(self):
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
        response = self.client.post(
            reverse('articles:review', kwargs={
                "slug": Article.objects.get().slug
            }),
            data={
                "review": {
                    "review_body": "I really liked the article",
                    "rating_value": 4
                }
            },
            format="json"
        )
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)