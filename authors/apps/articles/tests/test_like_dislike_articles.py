import json
from django.urls import reverse
from django.test import TestCase
from rest_framework import test, status

from authors.apps.authentication.models import User

class TestLikeArticles(TestCase):
    """
    this class houses test instances for like/dislike functionality 
    """
    def setUp(self):
        """
        this set ups the test class 
        """
        self.client = test.APIClient()
        self.client2 = test.APIClient()
        self.user = self.client.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "tworivers@gmail.com",
                    "username": "disliker",
                    "password": "usergeneration0"
                }
            },
            format="json"
        )

        verified_user = User.objects.get(username='disliker')
        verified_user.is_verified = True
        verified_user.save()
        self.user2 = self.client.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "tworivers2@gmail.com",
                    "username": "disliker2",
                    "password": "usergeneration0"
                }
            },
            format="json"
        )
        verified_user2 = User.objects.get(username='disliker2')
        verified_user2.is_verified = True
        verified_user2.save()
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
        self.login2 = self.client.post(
            reverse('authentication:user-login'),
            data={
                "user": {
                    "email": "tworivers2@gmail.com",
                    "password": "usergeneration0"
                }
            },
            format="json"
        )

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login.data['token'])
        self.client2.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login2.data['token'])

        new_article = self.client.post(
            reverse('articles:create-list'),
            data={
                "article": {
                    "title": "War of the roses",
                    "body": "Over a period of conflict between kin",
                    "description": "Written by yours truly",
                    "tags": ["religion", "nature", "film"]
                }
            },
            format="json"
        )
        new_article2 = self.client.post(
            reverse('articles:create-list'),
            data={
                "article": {
                    "title": "War of the roses",
                    "body": "Over a period of conflict between kin",
                    "description": "Written by yours truly",
                    "tags": ["religion", "nature", "film"]
                }
            },
            format="json"
        )
        article_result = json.loads(new_article.content)
        article_result2 = json.loads(new_article2.content)
        self.slug = article_result['article']['slug']
        self.slug2 = article_result2['article']['slug']

    def test_like_article(self):
        """Test whether authenticated user can like article"""
        response = self.client.post(
            reverse('articles:like-article',
            kwargs={'slug': self.slug}),
            format='json'
        )
        output = json.loads(response.content)
        self.assertIn(
            'you liked the article:',
            str(output))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_revoking_like(self):
        """Test whether authenticated user can revoke an article like"""
        self.client.post(
            reverse('articles:like-article',
            kwargs={'slug': self.slug}),
            format='json'
        )
        response = self.client.post(
            reverse('articles:like-article',
            kwargs={'slug': self.slug}),
            format='json'
        )
        output = json.loads(response.content)
        self.assertIn(
            'you have reverted your like for the article:',
            str(output))
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_dislike_article(self):
        """Test whether authenticated user can dislike article"""
        response = self.client.post(
            reverse('articles:dislike-article',
            kwargs={'slug': self.slug}),
            format='json'
        )
        output = json.loads(response.content)
        self.assertIn(
            'you disliked the article:',
            str(output))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_revoking_dislike(self):
        """Test whether authenticated user can revoke an article dislike"""
        self.client.post(
            reverse('articles:dislike-article',
            kwargs={'slug': self.slug}),
            format='json'
        )
        response = self.client.post(
            reverse('articles:dislike-article',
            kwargs={'slug': self.slug}),
            format='json'
        )
        output = json.loads(response.content)
        self.assertIn(
            'you have reverted your dislike for the article:',
            str(output))
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_liking_non_existent_article(self):
        """Test whether user can like an article that doesn't exist"""
        response = self.client.post(
            reverse('articles:like-article',
            kwargs={'slug': 'the_people_eater'}),
            format='json'
        )
        output = json.loads(response.content)
        self.assertIn(
            'The article requested does not exist',
            str(output))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_can_like_disliked_article(self):
        """
        Tests whether a user can change a dislike to a like
        """
        self.client.post(
            reverse('articles:dislike-article',
            kwargs={'slug': self.slug}),
            format='json'
        )
        response = self.client.post(
            reverse('articles:like-article',
            kwargs={'slug': self.slug}),
            format='json'
        )
        output = json.loads(response.content)
        self.assertIn(
            'you liked the article:',
            str(output))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_user_can_dislike_liked_article(self):
        """
        Tests whether a user can change a like to a dislike
        """
        self.client.post(
            reverse('articles:like-article',
            kwargs={'slug': self.slug}),
            format='json'
        )
        response = self.client.post(
            reverse('articles:dislike-article',
            kwargs={'slug': self.slug}),
            format='json'
        )
        output = json.loads(response.content)
        self.assertIn(
            'you disliked the article:',
            str(output))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_user_know_if_they_have_liked_article(self):
        """
        It tests that a user can know if they have already liked an article
        :return:
        """
        self.client.post(
            reverse('articles:like-article',
                    kwargs={'slug': self.slug}),
            format='json'
        )
        response = self.client.get(
            reverse('articles:liked-me',
                    kwargs={'slug': self.slug}),
            format='json'
        )
        response2 = self.client.get(
            reverse('articles:liked-me',
                    kwargs={'slug': 'the_people_eater'}),
            format='json'
        )
        response3 = self.client.get(
            reverse('articles:liked-me',
                    kwargs={'slug': self.slug2}),
            format='json'
        )
        output = json.loads(response2.content)
        self.assertIn(
            'The article requested does not exist',
            str(output))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'],
                         'You have reacted to this article before')
        self.assertEqual(response3.data['message'],
                         'You have not reacted to this article')

    def test_user_know_what_articles_they_have_liked_article(self):
            self.client.post(
                reverse('articles:like-article',
                        kwargs={'slug': self.slug}),
                format='json'
            )
            response = self.client.get(
                reverse('articles:liked-all'),
                format='json'
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['message'],
                             'You have reacted to these articles')

            response2 = self.client2.get(
                reverse('articles:liked-all'),
                format='json'
            )
            self.assertEqual(response2.data['message'],
                             'You have not reacted to any article')
