import jwt
from django.conf import settings
from rest_framework import authentication, exceptions
from .models import User
from .serializers import LoginSerializer
from .jwt_generator import jwt_decode


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        """
        Returns a `User` if a correct username and password have been supplied
        using HTTP Basic authentication.  Otherwise returns `None`.
        """

        raw_auth_token = authentication.get_authorization_header(request)
        auth_token = raw_auth_token.decode('utf-8').split()

        if not auth_token or auth_token[0].lower() != 'bearer':
            return None
        if len(auth_token) == 1:
            msg = ('Invalid basic header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth_token) > 2:
            msg = ('Invalid basic header.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            payload = jwt_decode(auth_token[1])

        except:
            msg = 'Invalid token. Please login'
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(payload)

    def authenticate_credentials(self, payload):
        """
        Confirm that the user_id in the payload belongs to
        an existing user
        """

        try:
            user = User.objects.get(id=payload['id'])

        except User.DoesNotExist:
            msg = 'User does not exist'
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')

        return (user, None)
