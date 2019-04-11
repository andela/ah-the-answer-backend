from django.test import TestCase
from django.urls import reverse
from rest_framework import test, status
from authors.apps.authentication.models import User
from authors.apps.articles.models import Article
from authors.apps.comments.models import Comment


class TestValidation(TestCase):
    def setUp(self):
        # User 1
        self.client = test.APIClient()
        self.user_signup = self.client.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "test@mail.com",
                    "username": "test",
                    "password": "test1234"
                }
            },
            format="json"
        )
        self.user = User.objects.get(
            email=self.user_signup.data.get('email')
        )
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
        self.token = self.login.data.get('token')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.article = Article.objects.create(
            title="Test title",
            body="This is a very awesome article on testing tests",
            description="Written by testing tester",
            author=self.user
        )

        # User 2
        self.client2 = test.APIClient()
        self.user_signup2 = self.client2.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "test2@mail.com",
                    "username": "test2",
                    "password": "test21234"
                }
            },
            format="json"
        )
        self.user2 = User.objects.get(
            email=self.user_signup2.data.get('email')
        )
        self.user2.is_verified = True
        self.user2.save()
        self.login2 = self.client2.post(
            reverse('authentication:user-login'),
            data={
                "user": {
                    "email": "test2@mail.com",
                    "password": "test21234"
                }
            },
            format="json"
        )
        self.token2 = self.login2.data.get('token')
        self.client2.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token2)

        # Create Comment
        self.comment = self.client.post(
            reverse(
                'comments:create-list',
                kwargs={
                    "slug": self.article.slug
                }
            ),
            data={
                "comment": {
                    "body": "This is a comment"
                }
            },
            format="json"
        )
        self.comment_id = self.comment.data.get('comment')['id']

    def test_update_comment_invalid_user(self):
        """
        Test that a comment is updated successfully
        """

        res = self.client2.put(
            reverse(
                'comments:details',
                kwargs={
                    "slug": self.article.slug,
                    'pk': self.comment_id
                }
            ),
            data={
                "comment": {
                    "body": "This is an updated comment"
                }
            },
            format="json"
        )

        self.assertEqual(self.comment.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_comment_invalid_user(self):
        """
        Test that a comment is updated successfully
        """

        res = self.client2.delete(
            reverse(
                'comments:details',
                kwargs={
                    "slug": self.article.slug,
                    'pk': self.comment_id
                }
            ),
            format="json"
        )

        self.assertEqual(self.comment.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_non_existent_comment(self):
        res = self.client.delete(
            reverse(
                'comments:details',
                kwargs={
                    "slug": self.article.slug,
                    'pk': self.comment_id
                }
            ),
            format="json"
        )

        res_after = self.client.delete(
            reverse(
                'comments:details',
                kwargs={
                    "slug": self.article.slug,
                    'pk': self.comment_id
                }
            ),
            format="json"
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res_after.status_code, status.HTTP_404_NOT_FOUND)
