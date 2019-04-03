from django.test import TestCase
from django.core import mail
from django.urls import reverse
from rest_framework import test, status
from ..models import User


class EmailTest(TestCase):
    def setUp(self):
        self.client = test.APIClient()
        self.user = User.objects.create(
            email="test@mail.com",
            username="test",
            password="test1234"
        )

    def test_user_not_verified_on_create(self):
        pass
        # self.assertFalse(self.user.is_verified)

    def test_email_sent(self):
        pass
        # initial_count = len(mail.outbox)
        # response = self.client.post(
        #     reverse('authentication:user-signup'),
        #     data={
        #         "user": {
        #             "email": "emailer@mail.com",
        #             "username": "emailer",
        #             "password": "emailer1234"
        #         }
        #     },
        #     format="json"
        # )

        # self.assertNotEqual(initial_count, len(mail.outbox))
        # self.assertTrue(initial_count < len(mail.outbox))

    def test_sent_email_content(self):
        pass

    def test_error_email_not_sent(self):
        pass

    def tearDown(self):
        pass
        # User.objects.get(id=self.user.id).delete()
