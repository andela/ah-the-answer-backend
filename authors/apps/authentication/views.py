import os
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .renderers import UserJSONRenderer
from .serializers import (
    LoginSerializer, RegistrationSerializer, UserSerializer, 
    PasswordResetSerializer, SetUpdatedPasswordSerializer
)
from authors.apps.authentication.jwt_generator import jwt_encode, jwt_decode
from authors.apps.core.utils import send_verification_email
from .models import User
from .backends import JWTAuthentication


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
        user_email = serializer.validated_data['email']
        username= serializer.validated_data['username']


        token = jwt_encode(user_email)
        template_name = 'email_verification.html'
        context = {'username': username, 'token': token, 'domain':os.getenv('DOMAIN')}

        html_message = render_to_string(template_name, context)
        subject = 'Please verify your email'
        response = send_verification_email(
            os.getenv('FROM_EMAIL'),
            user_email, subject, html_message
            )
        
        if not response:
            return Response(
                {
                   'error': 'something went wrong'
                },
                status=status.HTTP_400_BAD_REQUEST
                  )

        serializer.save()
        serializer.validated_data.pop('password')
        return Response(
            serializer.validated_data,
            status=status.HTTP_201_CREATED)


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

class EmailVerificationView(APIView):
    """This view handles request for verifying email adresses"""
    permission_classes = (AllowAny,)
    renderer_classes = (UserJSONRenderer,)
    serializer_class = UserSerializer

    def get(self, request, token):
        decoded_token = jwt_decode(token)
        email = decoded_token['user_id']
        if not email:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )

        #check if a user exists and if they are verified
        #if a user is not found we return an error
        #if we find a verified user , we raise an error

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'email': 'No user with email has been registered'},
                status=status.HTTP_404_NOT_FOUND
            )

        if user.is_verified is True:
            return Response(
                {'email': 'This email has already been verified'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.is_verified = True
        user.save()
        return Response(
            {'Success': 'Your email has been verified'}
        )
      
class PasswordResetAPIView(APIView):
    """
    This view handles the request for the password reset  link to be sent to the email
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
