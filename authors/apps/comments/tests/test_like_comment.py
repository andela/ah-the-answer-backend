import json
from django.urls import reverse
from django.test import TestCase
from rest_framework import test, status

from authors.apps.authentication.models import User
from authors.apps.articles.models import Article
from authors.apps.comments.models import Comment


class TestLikeComment(TestCase):
    """
    Test suite for liking a comment feature
    """

    def setUp(self):
        """
        Set up reusable parts of the test class
        """
        self.client = test.APIClient()
        self.user = User.objects.create_user(
            'disliker', 'tworivers@gmail.com',
            "usergeneration0"
        )

        self.user.is_verified = True
        self.user.save()
        self.login = self.client.post(
            reverse('authentication:user-login'),
            data={
                "user": {
                    "email": "tworivers@gmail.com",
                    "password": "usergeneration0"
                }
            },
            format="json"
        )

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login.data['token'])

        # create article
        self.article = Article.objects.create(
            title="Test title",
            body="This is a very awesome article on testing tests",
            description="Written by testing tester",
            author=self.user
        )
        # Create Comment
        self.comment = Comment.objects.create(article=self.article,
                                              body='I enjoyed your article',
                                              author=self.user)

        self.slug = self.article.slug

    def test_like_comment(self):
        """
        Test that an authenticated user can like a comment
        :return:
        """
        response = self.client.post(
            reverse('comments:like',
                    kwargs={
                        'pk': self.comment.id
                    }),
            format='json'
        )
        output = json.loads(response.content)
        self.assertIn('You liked comment:', str(output))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_reverting_like(self):
        """
        Tests that a user can revert on their previous like
        :param self:
        :return:
        """
        self.client.post(
            reverse('comments:like',
                    kwargs={
                        'pk': self.comment.id
                    }),
            format='json'
        )
        response = self.client.post(
            reverse('comments:like',
                    kwargs={
                        'pk': self.comment.id
                    }),
            format='json'
        )
        output = json.loads(response.content)
        self.assertIn('Your like has been reverted for comment:', str(output))
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_dislike_comment(self):
        """
        Test authenticated users can dislike a comment
        :return:
        """
        response = self.client.post(
            reverse('comments:dislike',
                    kwargs={
                        'pk': self.comment.id
                    }),
            format='json'
        )
        output = json.loads(response.content)
        self.assertIn('You disliked comment:', str(output))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_reverting_dislike(self):
        """
        Tests that a user can revert on their previous dislike
        :param self:
        :return:
        """
        self.client.post(
            reverse('comments:dislike',
                    kwargs={
                        'pk': self.comment.id
                    }),
            format='json'
        )
        response = self.client.post(
            reverse('comments:dislike',
                    kwargs={
                        'pk': self.comment.id
                    }),
            format='json'
        )
        output = json.loads(response.content)
        self.assertEqual('Your dislike has been reverted for comment: %s' % (
            self.comment.id), output['message'])
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_liking_non_existent_comment(self):
        """
        Tests that liking a non-existent comment fails
        :return:
        """
        response = self.client.post(
            reverse('comments:dislike',
                    kwargs={
                        'pk': 32434323342423423
                    }),
            format='json'
        )
        output = json.loads(response.content)
        self.assertIn('The comment does not exist', output['message'])
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_disliking_reverts_the_like_on_comment(self):
        """
        Tests when a user dislikes a comment they had already liked, that the
        like is reverted
        :return:
        """
        response1 = self.client.post(
            reverse('comments:like',
                    kwargs={
                        'pk': self.comment.id
                    }),
            format='json'
        )
        output1 = json.loads(response1.content)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        self.assertEqual(output1['likes'], 1)
        self.assertEqual(output1['dislikes'], 0)

        response2 = self.client.post(
            reverse('comments:dislike',
                    kwargs={
                        'pk': self.comment.id
                    }),
            format='json'
        )
        output = json.loads(response2.content)
        self.assertIn('You disliked comment: %s' % (self.comment.id,),
                      str(output['message']))
        self.assertEqual(output['likes'], 0)
        self.assertEqual(output['dislikes'], 1)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

    def test_get_likes_for_a_comment(self):
        """
        Test that the likes for a comment can be fetched
        :return:
        """
        self.client.post(
            reverse('comments:like',
                    kwargs={
                        'pk': self.comment.id
                    }),
            format='json'
        )

        response = self.client.get(
            reverse('comments:rating',
                    kwargs={
                        'pk': self.comment.id
                    }),
            format='json'
        )
        output = json.loads(response.content)
        self.assertEqual(output['likes'], 1)
        self.assertEqual(output['dislikes'], 0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_likes_for_a_nonexistent_comment(self):
        """
        Test that the likes for a non-existent comment will not be fetched
        :return:
        """
        self.client.post(
            reverse('comments:like',
                    kwargs={
                        'pk': self.comment.id
                    }),
            format='json'
        )

        response = self.client.get(
            reverse('comments:rating',
                    kwargs={
                        'pk': 999
                    }),
            format='json'
        )
        output = json.loads(response.content)
        self.assertEqual(output['message'], "The comment does not exist")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_if_user_has_liked_a_specific_comment(self):
        """
        Tests if a user has already liked/disliked a particular comment
        :return:
        """
        self.client.post(
            reverse('comments:like',
                    kwargs={
                        'pk': self.comment.id
                    }),
            format='json'
        )

        response = self.client.get(
            reverse('comments:check-rating',
                    kwargs={
                        'pk': self.comment.id,
                        'username': self.user.username
                    }),
            format='json'
        )
        output = json.loads(response.content)
        self.assertEqual(
            output['response'],
            "User has already liked/disliked this comment."
        )
        self.assertEqual(output['hasRated'], True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_if_user_has_not_liked_a_specific_comment(self):
        """
        Tests if a user has already liked/disliked a particular comment
        :return:
        """
        self.client.post(
            reverse('comments:like',
                    kwargs={
                        'pk': self.comment.id
                    }),
            format='json'
        )

        response = self.client.get(
            reverse('comments:check-rating',
                    kwargs={
                        'pk': 999,
                        'username': self.user.username
                    }),
            format='json'
        )
        output = json.loads(response.content)
        self.assertEqual(
            output['response'],
            "User has not liked/disliked this comment, or this comment does not exist."
        )
        self.assertEqual(output['hasRated'], False)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
