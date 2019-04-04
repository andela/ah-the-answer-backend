import json
from django.test import TestCase
from django.urls import reverse
from rest_framework import test, status
#from django.urls import reverse
#from rest_framework.test import APITestCase, APIClient
#from rest_framework.views import status
from ..models import User, ResetPasswordToken


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
        self.user_email = {"email": self.user.email}
        self.non_existent_email = {"email": "test@gmail.com"}
        self.invalid_email = {"email": "testgmail.com"}
        self.empty_email = {"email": ""}
        self.blank_email = {}
        self.password = {"password": "passwordreal"}
        self.short_password = {"password": "pass"}
        self.empty_password = {"password": ""}
        self.blank_password = {}
        self.valid_token = ''

    def test_existent_user(self):
        """
        Test that a valid user can send password reset request
        """
        response = self.client.post(
            reverse('authentication:password-reset'),
            self.user_email,
            format='json'
        )
        returned_data = json.loads(response.content)
        self.assertIn('Email sent to', str(returned_data))
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_non_existent_user(self):
        """
        tests that an invalid user cannot send password reset request 
        """
        response = self.client.post(
            reverse('authentication:password-reset'),
            self.non_existent_email,
            format='json'
        )
        returned_data = json.loads(response.content)
        self.assertIn('User with that email does not exist', str(returned_data))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_email(self):
        """
        tests that an invalid email address pattern cannot send request 
        """
        response = self.client.post(
            reverse('authentication:password-reset'),
            self.invalid_email,
            format='json'
        )
        returned_data = json.loads(response.content)
        self.assertIn('Enter a valid email address', str(returned_data))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_email_string(self):
        """
        tests that an empty string doesn't pass into the server 
        """
        response = self.client.post(
            reverse('authentication:password-reset'),
            self.empty_email,
            format='json'
        )
        returned_data = json.loads(response.content)
        self.assertIn('This field may not be blank', str(returned_data))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_empty_email_field(self):
        """
        tests that an empty email field is not sent as a request
        """
        response = self.client.post(
            reverse('authentication:password-reset'),
            self.blank_email,
            format='json'
        )
        returned_data = json.loads(response.content)
        self.assertIn('This field is required', str(returned_data))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_valid_password(self):
        """
        test for request with valid password
        """
        user = User.objects.get(email=self.user.email)
        token = user.get_reset_token(10)
        response = self.client.put(
            reverse('authentication:set-updated-password',
            kwargs={'reset_token': token}),
            self.password,
            format='json'
        )
        output = json.loads(response.content)
        self.assertIn('you may now log into your account with', str(output))
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

    def test_blank_password(self):
        """
        test for request with blank request object
        """
        user = User.objects.get(email=self.user.email)
        token = user.get_reset_token(10)
        response = self.client.put(
            reverse('authentication:set-updated-password',
            kwargs={'reset_token': token}),
            self.blank_password,
            format='json'
        )
        output = json.loads(response.content)
        self.assertIn('This field is required.', str(output))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_empty_password(self):
        """
        test for request with empty password value in JSON object
        """
        user = User.objects.get(email=self.user.email)
        token = user.get_reset_token(10)
        response = self.client.put(
            reverse('authentication:set-updated-password',
            kwargs={'reset_token': token}),
            self.empty_password,
            format='json'
        )
        output = json.loads(response.content)
        self.assertIn('This field may not be blank', str(output))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_short_password(self):
        """
        test for request with a short password
        """
        user = User.objects.get(email=self.user.email)
        token = user.get_reset_token(10)
        response = self.client.put(
            reverse('authentication:set-updated-password',
            kwargs={'reset_token': token}),
            self.short_password,
            format='json'
        )
        output = json.loads(response.content)
        self.assertIn('Ensure this field has at least 8 characters', str(output))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)