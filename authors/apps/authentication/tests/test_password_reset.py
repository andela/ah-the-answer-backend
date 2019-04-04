import json
from django.test import TestCase
from django.urls import reverse
from rest_framework import test, status
from ..models import User, ResetPasswordToken
from ..jwt_generator import jwt_encode

class TestPasswordResetRequest(TestCase):
    """
    tests password reset functionality
    """
    def setUp(self):
        self.client = test.APIClient()
        self.user = User.objects.create(
            email="Redhawk@gmail.com",
            password="fireandblood",
            username="doggetofthehill"
        )

    def test_existent_user(self):
        """
        Test that a valid user can send password reset request
        """
        user_email = {"email": self.user.email}
        response = self.client.post(
            reverse('authentication:password-reset'),
            user_email,
            format='json'
        )
        returned_data = json.loads(response.content)
        self.assertIn('Email sent to', str(returned_data))
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_non_existent_user(self):
        """
        tests that an invalid user cannot send password reset request 
        """
        non_existent_email = {"email": "test@gmail.com"}
        response = self.client.post(
            reverse('authentication:password-reset'),
            non_existent_email,
            format='json'
        )
        returned_data = json.loads(response.content)
        self.assertIn('User with that email does not exist', str(returned_data))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_email(self):
        """
        tests that an invalid email address pattern cannot send request 
        """
        invalid_email = {"email": "testgmail.com"}
        response = self.client.post(
            reverse('authentication:password-reset'),
            invalid_email,
            format='json'
        )
        returned_data = json.loads(response.content)
        self.assertIn('Enter a valid email address', str(returned_data))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_email_string(self):
        """
        tests that an empty string doesn't pass into the server 
        """
        empty_email = {"email": ""}
        response = self.client.post(
            reverse('authentication:password-reset'),
            empty_email,
            format='json'
        )
        returned_data = json.loads(response.content)
        self.assertIn('This field may not be blank', str(returned_data))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_email_field(self):
        """
        tests that an empty email field is not sent as a request
        """
        blank_email = {}
        response = self.client.post(
            reverse('authentication:password-reset'),
            blank_email,
            format='json'
        )
        returned_data = json.loads(response.content)
        self.assertIn('This field is required', str(returned_data))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_password(self):
        """
        test for request with valid password
        """
        password = {"password": "password12"}
        user = User.objects.get(email=self.user.email)
        token = jwt_encode(user_id=user.pk, days=10)
        response = self.client.put(
            reverse('authentication:set-updated-password',
            kwargs={'reset_token': token}),
            password,
            format='json'
        )
        output = json.loads(response.content)
        self.assertIn('you may now log into your account with', str(output))
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_blank_password(self):
        """
        test for request with blank request object
        """
        blank_password = {}
        user = User.objects.get(email=self.user.email)
        token = jwt_encode(user_id=user.pk, days=10)
        response = self.client.put(
            reverse('authentication:set-updated-password',
            kwargs={'reset_token': token}),
            blank_password,
            format='json'
        )
        output = json.loads(response.content)
        self.assertIn('This field is required.', str(output))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_empty_password(self):
        """
        test for request with empty password value in JSON object
        """
        empty_password = {"password": ""}
        user = User.objects.get(email=self.user.email)
        token = jwt_encode(user_id=user.pk, days=10)
        response = self.client.put(
            reverse('authentication:set-updated-password',
            kwargs={'reset_token': token}),
            empty_password,
            format='json'
        )
        output = json.loads(response.content)
        self.assertIn('This field may not be blank', str(output))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_short_password(self):
        """
        test for request with a short password
        """
        short_password = {"password": "pass"}
        user = User.objects.get(email=self.user.email)
        token = jwt_encode(user_id=user.pk, days=1)
        response = self.client.put(
            reverse('authentication:set-updated-password',
            kwargs={'reset_token': token}),
            short_password,
            format='json'
        )
        output = json.loads(response.content)
        self.assertIn('Ensure this field has at least 8 characters', str(output))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_aplhanumeric_password(self):
        """
        test for request with a short password
        """
        non_alphanumeric_password = {"password": "passwordtoday"}
        user = User.objects.get(email=self.user.email)
        token = jwt_encode(user_id=user.pk, days=1)
        response = self.client.put(
            reverse('authentication:set-updated-password',
            kwargs={'reset_token': token}),
            non_alphanumeric_password,
            format='json'
        )
        output = json.loads(response.content)
        self.assertIn('Please ensure your password contains at least one letter and one numeral', str(output))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

