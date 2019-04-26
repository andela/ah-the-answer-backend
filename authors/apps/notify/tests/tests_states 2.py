from django.test import TestCase
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import test, status
from authors.apps.authentication.models import User
from authors.apps.articles.models import Article, FavoriteModel
from authors.apps.notify.models import Notification
from authors.apps.notify.serializers import NotificationSerializer


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

    def test_read_unread(self):
        """
        Test user can retrieve the read or unread notifications
        """
        res1 = self.client.get(
            reverse(
                'notifications:read-unread-notifications',
                kwargs={"action": "read"}
            ),
        )

        res2 = self.client.get(
            reverse(
                'notifications:read-unread-notifications',
                kwargs={"action": "unread"}
            ),
        )

        notifs_read = Notification.objects.filter(is_read=True)
        notifs_unread = Notification.objects.filter(is_read=False)

        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertEqual(res2.status_code, status.HTTP_200_OK)

        self.assertEqual(
            res1.data['notifications'],
            NotificationSerializer(notifs_read, many=True).data
        )
        self.assertEqual(
            res2.data['notifications'],
            NotificationSerializer(notifs_unread, many=True).data
        )

    def test_read_unread_error(self):
        """
        Test displays error when invalid string entered in url
        """
        res = self.client.get(
            reverse(
                'notifications:read-unread-notifications',
                kwargs={"action": "error-read"}
            ),
        )

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_can_get_status_of_notification(self):
        """
        Test that the 'is_read' state of a notification is displayed
        """
        res = self.client.get(
            reverse(
                'notifications:state-notification',
                kwargs={'id': self.notification.id}
            )
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertFalse(res.data['is_read'])

    def test_can_update_status_of_notification(self):
        """
        Test that the 'is_read' state of a notification is updated
        """
        initial = self.notification.is_read
        res1 = self.client.put(
            reverse(
                'notifications:state-notification',
                kwargs={'id': self.notification.id}
            )
        )
        res2 = self.client.get(
            reverse(
                'notifications:state-notification',
                kwargs={'id': self.notification.id}
            )
        )
        res3 = self.client.put(
            reverse(
                'notifications:state-notification',
                kwargs={'id': self.notification.id}
            )
        )
        res4 = self.client.get(
            reverse(
                'notifications:state-notification',
                kwargs={'id': self.notification.id}
            )
        )

        self.assertEqual(res1.status_code, status.HTTP_200_OK)
        self.assertTrue(res2.data['is_read'])
        self.assertEqual(res2.status_code, status.HTTP_200_OK)
        self.assertFalse(res4.data['is_read'])

    def test_error_when_notification_non_existent(self):
        """
        Test that an error is raised when you try to get or put a non-existent
        notification
        """
        last = Notification.objects.last()
        res1 = self.client.get(
            reverse(
                'notifications:state-notification',
                kwargs={'id': (last.id + 1)}
            )
        )
        res2 = self.client.put(
            reverse(
                'notifications:state-notification',
                kwargs={'id': (last.id + 1)}
            )
        )

        self.assertEqual(res1.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(res2.status_code, status.HTTP_404_NOT_FOUND)

    def test_marks_all_notifications_as_read(self):
        """
        Test that a user can mark all notifications as read
        """
        notif2 = Notification.objects.create(
            body="Notification",
            recepient=self.user
        )
        res = self.client.put(
            reverse(
                'notifications:read-all-notifications'
            )
        )

        res_notif1 = self.client.get(
            reverse(
                'notifications:state-notification',
                kwargs={'id': self.notification.id}
            )
        )
        res_notif2 = self.client.get(
            reverse(
                'notifications:state-notification',
                kwargs={'id': notif2.id}
            )
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res_notif1.data['is_read'])
        self.assertTrue(res_notif2.data['is_read'])

    def test_deletes_all_notifications_as_read(self):
        """
        Test that a user can delete all notifications that have been read
        """
        notif1 = Notification.objects.create(
            body="Notification",
            recepient=self.user
        )
        notif2 = Notification.objects.create(
            body="Notification",
            recepient=self.user,
            is_read=True
        )

        res = self.client.delete(
            reverse(
                'notifications:read-all-notifications'
            )
        )

        res_notif1 = self.client.get(
            reverse(
                'notifications:state-notification',
                kwargs={'id': notif1.id}
            )
        )
        res_notif2 = self.client.get(
            reverse(
                'notifications:state-notification',
                kwargs={'id': notif2.id}
            )
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res_notif1.status_code, status.HTTP_200_OK)
        self.assertEqual(res_notif2.status_code, status.HTTP_404_NOT_FOUND)
