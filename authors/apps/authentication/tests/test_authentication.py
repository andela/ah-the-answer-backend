from django.test import TestCase
from django.urls import reverse
from rest_framework import test, status
from ..models import User
from ..jwt_generator import jwt_encode, jwt_decode
import json


class TestJWTGenerator(TestCase):
    def setUp(self):
        self.id = 11
        self.token = jwt_encode(self.id)
        self.client = test.APIClient()
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
        # Verify email
        test_user = User.objects.get(username='Bob')
        test_user.is_verified = True
        test_user.save()
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

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.login.data['token'])

    def test_that_token_encoded_decoded(self):
        decoded_id = jwt_decode(self.token)

        self.assertTrue(self.token)
        self.assertEqual(decoded_id['user_id'], self.id)

    def test_user_token_property(self):
        user = User.objects.create(
            username="test",
            email="test@mail.com",
            password="test123"
        )
        token = user.get_token

        self.assertTrue(token)
        self.assertEqual(jwt_decode(token)['user_id'], user.id)

    def test_login_endpoint(self):
        create_res = self.client.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "tester@mail.com",
                    "username": "tester",
                    "password": "tester1234"
                }
            },
            format="json"
        )
        # verify the user
        test_user = User.objects.get(username='tester')
        test_user.is_verified = True
        test_user.save()
        login_res = self.client.post(
            reverse('authentication:user-login'),
            data={
                "user": {
                    "email": "tester@mail.com",
                    "password": "tester1234"
                }
            },
            format="json"
        )

        self.assertEqual(create_res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(login_res.status_code, status.HTTP_200_OK)
        self.assertEqual(create_res.data['email'], login_res.data['email'])
        self.assertEqual(
            create_res.data['username'],
            login_res.data['username']
        )
        self.assertTrue(login_res.data['token'])

    def test_login_missing_fields(self):
        create_res = self.client.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "tester1@mail.com",
                    "username": "tester1",
                    "password": "tester1234"
                }
            },
            format="json"
        )
        response = self.client.post(
            reverse('authentication:user-login'),
            data={
                "user": {
                    "email": "tester1@mail.com"
                }
            },
            format="json"
        )

        self.assertEqual(create_res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_res.data['email'], 'tester1@mail.com')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data['errors'])

    def test_login_invalid_fields(self):
        create_res = self.client.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "tester11@mail.com",
                    "username": "tester11",
                    "password": "tester1234"
                }
            },
            format="json"
        )
        response = self.client.post(
            reverse('authentication:user-login'),
            data={
                "user": {
                    "email": "tester11@mail.com",
                    "password": "tester8978"
                }
            },
            format="json"
        )

        self.assertEqual(create_res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_res.data['email'], 'tester11@mail.com')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data['errors'])

    def test_login_non_existent_user(self):
        response = self.client.post(
            reverse('authentication:user-login'),
            data={
                "user": {
                    "email": "unknown@mail.com",
                    "password": "unk32134"
                }
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data['errors'])

    def test_login_incorrect_password_email_combination(self):
        create_res = self.client.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "newuser@mail.com",
                    "username": "newuser",
                    "password": "newuser1234"
                }
            },
            format="json"
        )
        response = self.client.post(
            reverse('authentication:user-login'),
            data={
                "user": {
                    "email": "newuser@mail.com",
                    "password": "wrongpass123"
                }
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data['errors'])

    def test_signup(self):
        response = self.client.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "tester2@mail.com",
                    "username": "tester2",
                    "password": "tester5678"
                }
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], 'tester2@mail.com')
        self.assertEqual(response.data['username'], 'tester2')

    def test_signup_missing_fields(self):
        response = self.client.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "tester2@mail.com",
                    "username": "tester2"
                }
            },
            format="json"
        )

        response2 = self.client.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "tester2@mail.com"
                }
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data['errors'])
        self.assertTrue(response.data['errors']['password'])
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response2.data['errors'])
        self.assertTrue(response2.data['errors']['username'])
        self.assertTrue(response2.data['errors']['password'])

    def test_empty_fields(self):
        response = self.client.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "",
                    "username": "tester2",
                    "password": ""
                }
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data['errors'])
        self.assertTrue(response.data['errors']['email'])
        self.assertTrue(response.data['errors']['password'])

    def test_user_already_exists(self):
        response = self.client.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "tester3@mail.com",
                    "username": "tester3",
                    "password": "tester321"
                }
            },
            format="json"
        )

        response2 = self.client.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "tester3@mail.com",
                    "username": "tester3",
                    "password": "tester321"
                }
            },
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['email'], 'tester3@mail.com')
        self.assertEqual(response.data['username'], 'tester3')
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response2.data['errors'])
        self.assertTrue(response2.data['errors']['username'])
        self.assertTrue(response2.data['errors']['email'])

    def test_get_users(self):
            response = self.client.get(reverse(
                'authentication:user-details',
            ),
                format="json")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
          
    def test_signup_nonalphanumeric_password(self):
        """
        test for request with a  non alphanumeric password
        """
        response = self.client.post(
            reverse('authentication:user-signup'),
            data={
                "user": {
                    "email": "tester3@mail.com",
                    "username": "tester3",
                    "password": "testetthhhhhkk"
                }
            },
            format="json"
        )
        output = json.loads(response.content)
        self.assertIn(
            'Please ensure your password contains at least one letter and one numeral', str(output)
                 )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

