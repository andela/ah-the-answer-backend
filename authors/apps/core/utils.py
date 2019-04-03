from datetime import datetime, timedelta
import jwt
from django.conf import settings
from rest_framework import exceptions

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

class TokenHandler:
    """This class contains the methods for creating custom
    tokens for users"""

    def create_verification_token(self, payload):
        """
        Create a JWT token to be sent in the verification
        email url
        """

        if not isinstance(payload, dict):
            raise TypeError('Payload must be a dictionary!')

        token_expiry = datetime.now() + timedelta(hours=24)

        try:
            token = jwt.encode({
                'email': payload['email'],
                'exp': int(token_expiry.strftime('%s'))},
                settings.SECRET_KEY, algorithm='HS256')
            return token.decode('utf-8')

        except KeyError:
            return "Please provide email"

    def validate_token(self, token):
        """
        Validate provided token. The email encoded in the token
        should be equal to the email of the user instance being
        passed.
        """

        try:
            decoded_token = jwt.decode(
                token, settings.SECRET_KEY, algorithm='HS256')

        except jwt.exceptions.ExpiredSignatureError:
            msg = 'Your token has expired. Make a new token and try again'
            raise exceptions.AuthenticationFailed(msg)

        except Exception:
            msg = 'Error. Could not decode token!'
            return msg

        return decoded_token

def send_verification_email(host_email, to, email_subject, content):
    message = Mail(
        from_email=host_email,
        to_emails=to,
        subject=email_subject,
        html_content=content)
    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        #print(response.status_code)
        #print(response.body)
        #print(response.headers
        return True
    except Exception as e:
        print(e.message)
        return False