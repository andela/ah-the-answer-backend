from rest_framework.views import APIView
from .models import Profile
from ..authentication.models import User
from django.shortcuts import get_object_or_404
from .serializers import ProfileSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.exceptions import APIException
from rest_framework.status import (
    HTTP_404_NOT_FOUND, HTTP_401_UNAUTHORIZED, HTTP_400_BAD_REQUEST)
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
import cloudinary


class CreateRetrieveProfileview(APIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request, username):
        """Returns a single user profile. Matches a profile
        based on the username."""
        user = User.objects.get(username=username)
        uid = user.pk
        profile = get_object_or_404(Profile.objects.all(), user_id=uid)
        serializer = ProfileSerializer(profile, many=False)
        return Response({"Profile": [serializer.data]}, status=200)

    def post(self, request):
        """Creates a single user profile"""
        try:
            profile = request.data.get('profile')
            serializer = ProfileSerializer(data=profile)
            if serializer.is_valid(raise_exception=True):
                profile_saved = serializer.save(user=self.request.user)
                return Response({"Success": "Profile for '{}' created successfully"
                                 .format(profile_saved.user)}, status=201)
            return Response('Profile creation failed. Request contains invalid'
                            'profile data. Ensure that your JSON profile payload '
                            'contains the following fields only: user_bio, '
                            'name, number_of_followers, number_following and'
                            'total_article. Also ensure that the user exists.')
        except IntegrityError:
            APIException.status_code = 400
            raise APIException({
                "errors": {
                    "Integrity Error": "A Profile for that User already exists"
                }
            })


class EditProfileView(APIView):
    """
    Edits a single profile of the currently logged in user
    Throws an Authorization error if user who did not create the profile,
    attempts edits
    """
    permission_classes = (IsAuthenticated, )

    def put(self, request, username):
        try:
            saved_profile = Profile.objects.select_related('user').get(
                user__username=username
            )
            if saved_profile.user != self.request.user:
                # validates ownership of the profile
                APIException.status_code = HTTP_401_UNAUTHORIZED
                raise APIException({
                    "errors": {
                        "Unauthorized": "You are not allowed\
                                        to edit this Profile"
                    }
                })
        except ObjectDoesNotExist:
            APIException.status_code = HTTP_404_NOT_FOUND
            raise APIException(
                {"message": "User with that profile does not exist"})

        data = request.data.get('profile')
        serializer = ProfileSerializer(
            instance=saved_profile, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            profile_saved = serializer.save()
        return Response(
            {
                "success": "Profile updated successfully",
                "profile": serializer.data
            },
            status=200
        )


class AvatarView(APIView):
    """
    Makes partioal edits to the profile to change the avatar to a desired one
    Throws an Authorization error if user who did not create the profile,
    attempts edits
    """
    permission_classes = (IsAuthenticated, )
    # checks whether user is logged in

    def patch(self, request, username):
        try:
            # retrieves user object throws error if profile is in-existent
            saved_profile = Profile.objects.select_related('user').get(
                user__username=username
            )
        except ObjectDoesNotExist:
            APIException.status_code = HTTP_404_NOT_FOUND
            raise APIException(
                {"message": "User with that profile does not exist"})

        if saved_profile.user != self.request.user:
            APIException.status_code = HTTP_401_UNAUTHORIZED
            raise APIException({
                "errors": {
                    "Unauthorized": "You are not allowed to edit this Profile"
                }
            })
        try:
            avatar_data = str(request.data.get('avatar'))
            if not avatar_data.lower().endswith((".png", ".jpg", ".jpeg")):
                raise APIException(
                    {"message": "This is an invalid avatar format"})
            data = {"avatar": request.data.get('avatar')}
            serializer = ProfileSerializer(
                instance=saved_profile, data=data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
            return Response(
                {
                    "success": "Profile avatar was updated successfully"
                }, status=200)
        except Exception as e:
            APIException.status_code = HTTP_400_BAD_REQUEST
            raise APIException({
                "errors": str(e)
            })
