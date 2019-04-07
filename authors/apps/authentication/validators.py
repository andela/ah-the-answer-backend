import os
from google.oauth2 import id_token
from google.auth.transport import requests


import facebook
import twitter
from github import Github


class GoogleValidate:
    """
    Core class to verify and decode auth tokens to return user data
    """

    @staticmethod
    def validate_google_token(access_token):
        """
            - Get the access token and verifires that it is valid by checking with google in the \
             id_token.verify_oauth2_token method 
            - This requests takes in the CLIEND_ID of the app that the token is authenticating too 
        """
        
        try:
            # TODO figue why id_token return error `target audience invalid` 
            # despite specifying the correct CLIENT_ID for authors haven.
            decoded_google_user_info = id_token.verify_oauth2_token(
                access_token, requests.Request(),
                os.getenv('SOCIAL_AUTH_GOOGLE_OAUTH2_KEY'))
           
            decoded_google_user_info
        except ValueError:
            decoded_google_user_info = None
        return decoded_google_user_info


class FacebookValidate:
    """
    This class contains a method that handles both the verifications and decoding
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
            user_data_from_fb
        except:
            user_data_from_fb = None

        return user_data_from_fb


class TwitterValidate:
    """Utilizes pytwitter package, this solution requires verifying the identity of the
    acces token using twitter API to get the details of the authorized user."""
    @staticmethod
    def extract_tokens(access_tokens):
   
        access_tokens = access_tokens.split(' ')
        if len(auth_tokens) < 2:
            return 'invalid token', 'invalid token'
        access_token_key = auth_tokens[0]
        access_token_secret = auth_tokens[1]

        return access_token_key, access_token_secret

    @staticmethod
    def validate_twitter_token(access_tokens):
    
        access_token_key, access_token_secret = TwitterValidate.extract_tokens(
            access_tokens)

        try:
            consumer_key = os.getenv('SOCIAL_AUTH_TWITTER_KEY')
            consumer_secret = os.getenv('SOCIAL_AUTH_TWITTER_SECRET')
            api = twitter.Api(
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                access_token_key=access_token_key,
                access_token_secret=access_token_secret
            )
            user_data_from_twitter = api.VerifyCredentials(include_email=True)
            return user_data_from_twitter.__dict__

        except:
            return None

