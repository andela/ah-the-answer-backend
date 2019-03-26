import jwt
from django.conf import settings
from rest_framework import authentication, exceptions
from .models import User
from .serializers import LoginSerializer
from .jwt_generator import jwt_decode


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request, username=None, password=None):
        """
        Returns a `User` if a correct username and password have been supplied
        using HTTP Basic authentication.  Otherwise returns `None`.
        """

        auth_token = request.META.get('HTTP_AUTHORIZATION', b'').split()

        if not auth_token or auth_token[0].lower() != 'bearer':
            return None
        if len(auth_token) == 1:
            msg = ('Invalid basic header. No credentials provided.')
            raise exceptions.AuthenticationFailed(msg)
        elif len(auth_token) > 2:
            msg = ('Invalid basic header.')
            raise exceptions.AuthenticationFailed(msg)

        try:
            payload = jwt.decode(auth_token[1])
        except:
            msg = 'Invalid token. Please login'
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(payload, password, request)

    def authenticate_credentials(self, payload, password):
        """
        Authenticate the user.username and password against username and
        password with optional request for context.
        """

        try:
            user = User.objects.get(id=payload['user_id'])
            valid_user = authenticate(
                username=user.username,
                password=password
            )
        except User.DoesNotExist:
            msg = 'User does not exist'
            raise exceptions.AuthenticationFailed(msg)

        if valid_user is None:
            raise exceptions.AuthenticationFailed('Invalid username/password.')

        if not valid_user.is_active:
            raise exceptions.AuthenticationFailed('User inactive or deleted.')

        return (valid_user, None)
