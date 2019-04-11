from django.test import TestCase
from rest_framework import test, status
from unittest.mock import Mock, patch
from ..validators import FacebookValidate, GoogleValidate, TwitterValidate
import json


class SocialAuthTest(TestCase):
    def setUp(self):
        self.client = test.APIClient()

    def create_user(self, username, email, pwd):
        self.client.post('/api/user/', {
            "username": username,
            "email": email,
            "pwd": pwd
        }, format='json')

    # FACEBOOK
    def test_facebook_validate_token_is_called(self):
        with patch(
                'authors.apps.authentication.validators.facebook.GraphAPI') \
                as mock_facebook_validate:
            FacebookValidate.validate_facebook_token('access token')
            self.assertTrue(mock_facebook_validate.called)
            mock_facebook_validate.assert_called_with(
                access_token='access token', version='3.1')

    def test_verify_facebook_auth_raises_exception_on_invalid_token(self):
        with patch(
                'authors.apps.authentication.validators.facebook.GraphAPI') \
                as mock_facebook_validate:
            FacebookValidate.validate_facebook_token('token')
            mock_facebook_validate.side_effect = ValueError
            self.assertRaises(ValueError, mock_facebook_validate)
            self.assertIsNone(
                FacebookValidate.validate_facebook_token('token'))

    def test_facebook_validate_returns_correct_data_for_valid_tokens(self):
        facebook_user_info_valid_response = {
            "name": "Dick Alceejfaafeif Bowerssky",
            "email": "bcmeordvda_1554574357@tfbnw.net",
            "id": "102723377587866"}
        with patch(
                'authors.apps.authentication.validators.facebook.GraphAPI') \
                as mock_facebook_validate:
            mock_facebook_validate.return_value = \
                facebook_user_info_valid_response
            self.assertEqual(mock_facebook_validate(
                'VALID facebook token'), facebook_user_info_valid_response)

    def test_facebook_login_valid_token(self):
        with patch(
                'authors.apps.authentication.validators.FacebookValidate'
                '.validate_facebook_token') as mock_facebook_validate:
            mock_facebook_validate.return_value = {
                "name": "Dick Alceejfaafeif Bowerssky",
                "email": "bcmeordvda_1554574357@tfbnw.net",
                "id": "102723377587866"}
            mock_facebook_validate('token')
            res = self.client.post(
                '/api/users/facebook/',
                {"access_token": "valid token for facebook"},
                format='json')
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertIn("token", json.loads(res.content)['user'])

    def test_facebook_user_with_attached_email_already_exists_in_db(self):
        self.create_user('Dick', 'cmeordvda_1554574357@tfbnw.net',
                         'pwd!@#42go')
        with patch(
                'authors.apps.authentication.validators'
                '.FacebookValidate.validate_facebook_token') as \
                mock_facebook_validate:
            mock_facebook_validate.return_value = {
                "name": "Dick", "email": "cmeordvda_1554574357@tfbnw.net",
                "id": "102723377587866"}
            res = self.client.post(
                '/api/users/facebook/',
                {"access_token": "valid token for facebook"},
                format='json')
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertIn("token", json.loads(res.content)['user'])

    # GOOGLE

    def test_google_validate_token_is_called(self):
        with patch(
                'authors.apps.authentication.validators.id_token'
                '.verify_oauth2_token') as mock_google_validate:
            GoogleValidate.validate_google_token('access token')
            self.assertTrue(mock_google_validate.called)

    def test_verify_google_auth_raises_exception_on_invalid_token(self):
        with patch(
                'authors.apps.authentication.validators.id_token'
                '.verify_oauth2_token') as mock_google_validate:
            GoogleValidate.validate_google_token('token')
            mock_google_validate.side_effect = ValueError
            self.assertRaises(ValueError, mock_google_validate)
            self.assertIsNone(GoogleValidate.validate_google_token('token'))

    def test_google_validate_returns_correct_data_when_token_is_valid(self):
        google_user_info_valid_response = {
            "name": "Dick", "email": "dick32424@gmail.com",
            "sub": "102723377587866"}
        with patch(
                'authors.apps.authentication.validators'
                '.GoogleValidate.validate_google_token') as \
                mock_google_validate:
            mock_google_validate.return_value = google_user_info_valid_response
            self.assertEqual(mock_google_validate(
                'VALID google token'), google_user_info_valid_response)

    def test_google_validate_returns_none_on_invalid_token(self):
        with patch(
                'authors.apps.authentication.validators'
                '.GoogleValidate.validate_google_token') as \
                mock_google_validate:
            mock_google_validate.return_value = None
            self.assertIsNone(mock_google_validate('INVALID google token'))

    def test_google_user_with_attached_email_already_exists_in_db(self):
        self.create_user('Dick ', 'dick32424@gmail.com',
                         'pwd!@#42go')
        with patch(
                'authors.apps.authentication.validators'
                '.GoogleValidate.validate_google_token') as \
                mock_google_validate:
            mock_google_validate.return_value = {
                "name": "Dick", "email": "dick32424@gmail.com",
                "sub": "102723377587866"}
            res = self.client.post(
                '/api/users/google/',
                {"access_token": "valid token for google"},
                format='json')
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertIn("token", json.loads(res.content)['user'])

    def test_google_login_valid_token(self):
        with patch(
                'authors.apps.authentication.validators'
                '.GoogleValidate.validate_google_token') as \
                mock_google_validate:
            mock_google_validate.return_value = {
                "name": "Dick", "email": "dick32424@gmail.com",
                "sub": "102723377587866"}
            res = self.client.post(
                '/api/users/google/',
                {"access_token": "valid token for google"},
                format='json')
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertIn("token", json.loads(res.content)['user'])

    # TWITTER
    def test_twitter_validate_token_is_called(self):
        with patch(
                'authors.apps.authentication.validators'
                '.OAuth1Session.get') as mock_twitter_validate:
            TwitterValidate.validate_twitter_token('access token')
            self.assertTrue(mock_twitter_validate.called)

    def test_verify_twitter_auth_raises_exception_when_token_is_invalid(self):
        with patch(
                'authors.apps.authentication.validators'
                '.OAuth1Session.get') as mock_twitter_validate:
            TwitterValidate.validate_twitter_token(
                'access_token1 access_token2')
            mock_twitter_validate.side_effect = ValueError
            self.assertRaises(ValueError, mock_twitter_validate)
            self.assertIsNone(TwitterValidate.validate_twitter_token('token'))

    def test_twitter_validate_returns_correct_data_when_token_is_valid(self):
        twitter_user_info_valid_response = {
            "name": "Dick", "email": "dick32424@twitter.com",
            "id_str": "102723377587866"}
        with patch(
                'authors.apps.authentication.validators'
                '.OAuth1Session.get') as \
                mock_twitter_validate:
            mock_twitter_validate.return_value = \
                twitter_user_info_valid_response
            self.assertEqual(mock_twitter_validate(
                'VALID token'), twitter_user_info_valid_response)

    def test_twitter_validate_returns_none_on_invalid_token(self):
        with patch(
                'authors.apps.authentication.validators'
                '.OAuth1Session.get') as \
                mock_twitter_validate:
            mock_twitter_validate.return_value = None
            self.assertIsNone(mock_twitter_validate('INVALID twitter token'))

    def test_twitter_login_invalid_token(self):
        with patch(
                'authors.apps.authentication.validators'
                '.OAuth1Session.get') as \
                mock_twitter_validate:
            mock_twitter_validate.return_value = None
            res = self.client.post(
                '/api/users/twitter/', {"access_token": "valid token"},
                format='json')
            self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(json.loads(res.content), {"errors": {
                "access_token": ["Invalid token please try again"]}})

    def test_twitter_user_with_attached_email_already_exists_in_db(self):
        self.create_user('Dick ', 'dick32424@twitter.com',
                         'pwd!@#42go')
        with patch(
                'authors.apps.authentication.validators'
                '.TwitterValidate.validate_twitter_token') as \
                mock_google_validate:
            mock_google_validate.return_value = {
                "name": "Dick", "email": "dick32424@twitter.com",
                "id_str": "102723377587866", "screen_name": "fadfdf"}
            res = self.client.post(
                '/api/users/twitter/',
                {"access_token": "valid token for twitter"},
                format='json')
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            self.assertIn("token", json.loads(res.content)['user'])
