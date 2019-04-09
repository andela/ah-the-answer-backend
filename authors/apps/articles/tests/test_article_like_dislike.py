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
        
        new_article = self.client.post(
            reverse('articles:create-list'),
            data={
                "article": {
                    "title": "War of the roses",
                    "body": "Over a period of conflict between kin",
                    "description": "Written by yours truly",
                }
            },
            format="json"
        )
        article_result = json.loads(new_article.content)
        self.slug = article_result['article']['slug']

    def test_like_article(self):
        """Test whether authenticated user can like article"""
        response = self.client.post(
            reverse('articles:like-article',
            kwargs={'slug': self.slug}),
            format='json'
        )
        output = json.loads(response.content)
        self.assertIn(
            'you liked {} article'.format(self.slug),
            str(output))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_revoking_like_dislike(self):
        """Test whether authenticated user can revoke (dis)like article"""
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
            'you have reverted your like/dislike for {} article'.format(self.slug),
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
            'you have disliked {} article'.format(self.slug),
            str(output))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_liking_non_existent_article(self):
        """Test whether user can like an article that doesn't exist"""
        response = self.client.post(
            reverse('articles:like-article',
            kwargs={'slug': 'the_people_eater'}),
            format='json'
        )
        output = json.loads(response.content)
        self.assertIn(
            'Article requested does not exist',
            str(output))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
