from rest_framework import status, serializers
from rest_framework.generics import RetrieveUpdateAPIView, GenericAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer,
    PasswordResetSerializer, SetUpdatedPasswordSerializer, 
    GoogleAuthSerializer, FacebookAuthSerializer,
    TwitterAuthSerializer
)
from social_django.utils import load_backend, load_strategy

from social_core.backends.oauth import BaseOAuth1, BaseOAuth2
from social_core.exceptions import MissingBackend

from .models import User
from .backends import JWTAuthentication
from .jwt_generator import jwt_decode

from .validators import GoogleValidate
class RegistrationAPIView(APIView):
    # Allow any user (authenticated or not) to hit this endpoint.
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # The create serializer, validate serializer, save serializer pattern
        # below is common and you will see it a lot throughout this course and
        # your own work later on. Get familiar with it.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})

        # Notice here that we do not call `serializer.save()` like we did for
        # the registration endpoint. This is because we don't actually have
        # anything to save. Instead, the `validate` method on our serializer
        # handles everything we need.
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def retrieve(self, request, *args, **kwargs):
        # There is nothing to validate or save here. Instead, we just want the
        # serializer to handle turning our `User` object into something that
        # can be JSONified and sent to the client.
        serializer = self.serializer_class(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer_data = request.data.get('user', {})

        # Here is that serialize, validate, save pattern we talked about
        # before.
        serializer = self.serializer_class(
            request.user, data=serializer_data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class PasswordResetAPIView(APIView):
    """
    This view handles the request for the password reset  link to be sent to
    the email
    """
    permission_classes = (AllowAny,)

    def post(self, request):
        """POST request for the password reset functionality"""
        serializer = PasswordResetSerializer(data=request.data)
        sent_email = User.dispatch_reset_token(serializer, request)
        return Response({
            'message': sent_email
        }, status=status.HTTP_202_ACCEPTED)


class SetUpdatedPasswordAPIView(APIView):
    """
    this view handles PUT request for setting new login password
    """
    permission_classes = (AllowAny,)

    def put(self, request, reset_token):
        serializer = SetUpdatedPasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            new_password = request.data['password']
            payload = jwt_decode(reset_token)
            user_details = JWTAuthentication().authenticate_credentials(payload)
            output = User.persist_new_password(user_details, new_password)
            return Response(
                {'message': output},
                status=status.HTTP_202_ACCEPTED
            )


class GoogleAuthView(GenericAPIView):
    """
        Google authentication view access view
    """
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = GoogleAuthSerializer

    def post(self, request):
        serializer = GoogleAuthSerializer(data={
            'access_token': request.data.get('access_token', {})
            })
        serializer.is_valid(raise_exception=True)
        serializer
        return Response({
            "token": serializer},
            status=status.HTTP_200_OK)


class FacebookAuthAPIView(GenericAPIView):
    """
        Facebook authentication view access view
    """
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = FacebookAuthSerializer

    def post(self, request):
        serializer = self.serializer_class(data={
            'access_token': request.data.get('access_token', {})})
        serializer.is_valid(raise_exception=True)
        res = {"token": serializer.data['access_token']}
        return Response(res, status=status.HTTP_200_OK)


class TwitterAuthAPIView(GenericAPIView):
    """
        Twitter authentication view access view
    """
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = TwitterAuthSerializer

    def post(self, request):
        token = request.data.get('access_token', {})
        serializer = self.serializer_class(data={'access_token': token})
        serializer.is_valid(raise_exception=True)
        res = {"token": serializer.data['access_token']}
        return Response(res, status=status.HTTP_200_OK)
