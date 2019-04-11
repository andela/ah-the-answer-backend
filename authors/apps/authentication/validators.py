import os
import json

from google.oauth2 import id_token
from google.auth.transport import requests

import facebook
from requests_oauthlib import OAuth1Session


class GoogleValidate:
    """
    Core class to verify and decode auth tokens to return user data
    """

    @staticmethod
    def validate_google_token(access_token):
        """
            - Get the access token and verifies that it is valid by
            checking with google in the  `id_token.verify_oauth2_token` method
            - This requests takes in the CLIENT_ID of the app that the token
            is authenticating too
        """

        try:
            decoded_google_user_info = id_token.verify_oauth2_token(
                access_token, requests.Request(),
                os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY'))
        except ValueError:
            decoded_google_user_info = None
        return decoded_google_user_info


class FacebookValidate:
    """
    This class contains a method that handles both the verifications and
    decoding
    of the facebook access_token and returns decoded user data
    """

    @staticmethod
    def validate_facebook_token(token):
        """
        This method utilizes the graph api (when passed an access_token) from 
        the facebook sdk to call for ask for user data
        """
        try:
            graph = facebook.GraphAPI(access_token=token, version="3.1")
            user_data_from_fb = graph.request(
                '/me?fields=id,name,email')
        except:
            user_data_from_fb = None

        return user_data_from_fb


class TwitterValidate:
    """Utilizes python-twitter package, this solution requires verifying the
    identity of the access token using twitter API to get the details of the
    authorized user."""

    @staticmethod
    def extract_tokens(access_tokens):

        access_tokens = access_tokens.split(' ')
        if len(access_tokens) < 2:
            return 'invalid token', 'invalid token'
        access_token_key = access_tokens[0]
        access_token_secret = access_tokens[1]

        return access_token_key, access_token_secret

    @staticmethod
    def validate_twitter_token(access_tokens):
        verify_url = 'https://api.twitter.com/1.1/account/verify_credentials' \
                     '.json'
        access_token_key, access_token_secret = TwitterValidate.extract_tokens(
            access_tokens)
        try:
            twitter = OAuth1Session(
                client_key=os.getenv('SOCIAL_AUTH_TWITTER_KEY'),
                client_secret=os.getenv('SOCIAL_AUTH_TWITTER_SECRET'),
                resource_owner_key=access_token_key,
                resource_owner_secret=access_token_secret)
            raw_data_from_twitter = twitter.get(
                verify_url + '?include_email=true')
            user_data_from_twitter = json.loads(raw_data_from_twitter.text)
        except:
            return None
        return user_data_from_twitter
