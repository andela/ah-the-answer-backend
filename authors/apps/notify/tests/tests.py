from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import test, status
from authors.apps.authentication.models import User
from authors.apps.articles.models import Article, FavoriteModel
from authors.apps.notify.models import Notification
from authors.apps.notify.serializers import NotificationSerializer


class TestModel(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="test@mail.com",
            username="test",
            password="test1234"
        )
        self.notification = Notification.objects.create(
            body="Notification",
            recepient=self.user
        )

    def test_notification_model(self):
        """
        Test that a notification is created and
        the __str__ has only 10 characters
        """
        self.assertTrue(self.notification)
        self.assertEqual(len(self.notification.__str__()), 10)


class TestAPI(TestCase):
    def setUp(self):

        # Authentication
        self.client = test.APIClient()
        self.client2 = test.APIClient()
        self.user = User.objects.create_user(
            email="test@mail.com",
            username="test",
            password="test1234"
        )
        self.follower = User.objects.create_user(
            email="follower@mail.com",
            username="follower",
            password="follower1234"
        )
        self.notification = Notification.objects.create(
            body="Notification",
            recepient=self.user
        )
        self.token = self.user.get_token
        self.token2 = self.follower.get_token
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token)
        self.client2.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token2)

        # Create profiles
        self.user_profile = self.client.post(
            reverse('profile:profile-create'),
            data={
                "profile": {
                    "user_bio": "I love passing as a test",
                    "name": "Test Tester"
                }
            },
            format="json"
        )

        self.follower_profile = self.client2.post(
            reverse('profile:profile-create'),
            data={
                "profile": {
                    "user_bio": "I love Following people",
                    "name": "Test Tester"
                }
            },
            format="json"
        )

        # Follow test user
        self.follow_user = self.client2.post(
            reverse(
                'follow:follow-user',
                kwargs={'user_to_follow': self.user.username}
            ),
            format="json"
        )

    def test_get_all_notifications(self):
        """
        Test that a user can get all their notifications
        """
        res = self.client.get(
            reverse('notifications:all-notifications'),
        )
        notifications = Notification.objects.all()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data['notifications'],
            NotificationSerializer(notifications, many=True).data
        )

    def test_get_one_notification(self):
        """
        Test that a user can get one notification
        """
        res = self.client.get(
            reverse(
                'notifications:detail-notification',
                kwargs={'id': self.notification.id}
            ),
            format="json"
        )

        notification = Notification.objects.get(id=self.notification.id)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data['notifications'],
            NotificationSerializer(notification).data
        )

    def test_get_one_non_existent_notification(self):
        """
        Test that an error is raised if the notification does not exist
        """

        Notification.objects.get(id=self.notification.id).delete()
        res = self.client.get(
            reverse(
                'notifications:detail-notification',
                kwargs={'id': self.notification.id}
            ),
            format="json"
        )

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertRaises(ObjectDoesNotExist)

    def test_notification_created_article(self):
        """
        Test that a notification is sent when an article is created
        """
        Notification.objects.all().delete()
        article = self.client.post(
            reverse('articles:create-list'),
            data={
                "article": {
                    "title": "Test title",
                    "body": "This is a very awesome article on testing tests",
                    "description": "Written by testing tester",
                    "tags": []
                }
            },
            format="json"
        )

        res = self.client2.get(
            reverse('notifications:all-notifications'),
        )
        notification = Notification.objects.first()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data['notifications'][0],
            NotificationSerializer(notification).data
        )

    def test_notification_created_comment(self):
        """
        Test that a notification is sent when a user comments on an article
        """
        Notification.objects.all().delete()
        user = User.objects.create_user(
            email="newuser@mail.com",
            username="newuser",
            password="newuser1234"
        )
        article = Article.objects.create(
            title="Test title",
            body="This is a very awesome article on testing tests",
            description="Written by testing tester",
            tags=[],
            author=user
        )
        favourite_article = FavoriteModel.objects.create(
            user=self.user,
            article=article,
            favorite=True
        )

        comment = self.client2.post(
            reverse(
                'comments:create-list',
                kwargs={
                    "slug": article.slug
                }
            ),
            data={
                "comment": {
                    "body": "This is a comment"
                }
            },
            format="json"
        )

        res = self.client.get(
            reverse('notifications:all-notifications'),
        )
        notification = Notification.objects.get()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(
            res.data['notifications'][0],
            NotificationSerializer(notification).data
        )

    def test_can_get_subscription(self):
        """
        Test that a user can check the status of their subscription
        """
        res = self.client.get(
            reverse('notifications:subscription')
        )

        self.assertTrue(res.data.get('subscription')['status'])

    def test_unsubscribe_email(self):
        """
        Test that a user can unsubscribe from email notifications
        """
        res = self.client.post(
            reverse('notifications:subscription')
        )

        status = self.client.get(
            reverse('notifications:subscription')
        )

        self.assertFalse(status.data.get('subscription')['status'])

    def test_can_resubscribe_email(self):
        """
        Test that a user can subscribe to email notifications
        after unsubscribing
        """
        res = self.client.post(
            reverse('notifications:subscription')
        )

        status = self.client.get(
            reverse('notifications:subscription')
        )

        res2 = self.client.post(
            reverse('notifications:subscription')
        )
        status2 = self.client.get(
            reverse('notifications:subscription')
        )

        self.assertFalse(status.data.get('subscription')['status'])
        self.assertTrue(status2.data.get('subscription')['status'])
