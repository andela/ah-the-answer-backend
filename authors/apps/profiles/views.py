from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema


import cloudinary

from .models import Profile
from ..authentication.models import User
from .serializers import ProfileSerializer


class ProfilesListAPIview(APIView):
    """This class allows authenticated users to get all profiles"""
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        profiles = Profile.objects.all()
        serializer = ProfileSerializer(profiles, many=True)
        if not profiles:
            return Response(
                {"message": "No profile available"}
            )
        return Response({"profiles": serializer.data})


class CreateRetrieveProfileView(APIView):
    """Implements two user profile related views. The 'get' view fetches a single
    profile from the database and the 'post' view creates a single user
    profile."""
    permission_classes = (IsAuthenticated,)

    def get(self, request, username):
        """Returns a single user profile. Matches a profile
        based on the username."""
        user = User.objects.get(username=username)
        uid = user.pk
        profile = get_object_or_404(Profile.objects.all(), user_id=uid)
        serializer = ProfileSerializer(profile, many=False)
        return Response({"profile": serializer.data})

    @swagger_auto_schema(request_body=ProfileSerializer,
                         responses={201: ProfileSerializer(),
                                    400: "Bad Request",
                                    403: "Forbidden",
                                    404: "Not Found"})
    def post(self, request):
        """Creates and saves a single user profile to the database. Checks if
        a profile already exits for the current user."""
        user_check = self.request.user
        if Profile.objects.filter(user=user_check).exists():
            return Response('A profile for this user already exists. Please '
                            'choose a new user to create a profile.',
                            status=status.HTTP_400_BAD_REQUEST)
        profile = request.data.get('profile')
        serializer = ProfileSerializer(data=profile)
        if serializer.is_valid(raise_exception=True):
            profile_saved = serializer.save(user=self.request.user)
            return Response({"success": "Profile for '{}' created successfully"
                             .format(profile_saved)},
                            status=status.HTTP_201_CREATED)
        return Response('Invalid data. Ensure your profile '
                        'payload corresponds to the profile.serializers '
                        'fields.', status=status.HTTP_400_BAD_REQUEST)


class EditProfileView(APIView):
    """
    View for updating a Users' profile
    User editing the profile must be its creator
    """

    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(request_body=ProfileSerializer,
                         responses={201: ProfileSerializer(),
                                    400: "Bad Request",
                                    403: "Forbidden",
                                    404: "Not Found"})
    def put(self, request, username):
        try:
            saved_profile = Profile.objects.select_related('user').get(
                user__username=username
            )
            if saved_profile.user != self.request.user:
                # validates ownership of the profile
                APIException.status_code = status.HTTP_401_UNAUTHORIZED
                raise APIException({
                    "errors": {
                        "Unauthorized": "You are not allowed to edit this Profile"
                    }
                })
        except ObjectDoesNotExist:
            APIException.status_code = status.HTTP_404_NOT_FOUND
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
    Makes partial edits to the profile to change the avatar to a desired one
    Throws an Authorization error if the user who did not create the profile,
    attempts edits
    """
    # permission_classes = (IsAuthenticated, ) # only authenticated users can access this route

    @swagger_auto_schema(request_body=ProfileSerializer,
                         responses={201: ProfileSerializer(),
                                    400: "Bad Request",
                                    403: "Forbidden",
                                    404: "Not Found"})
    def patch(self, request, username):
        try:
            # retrieves user object throws error if profile is in-existent
            saved_profile = Profile.objects.select_related('user').get(
                user__username=username
            )
        except ObjectDoesNotExist:
            # raises an exception if user object does not exist
            APIException.status_code = status.HTTP_404_NOT_FOUND
            raise APIException(
                {"message": "User with that profile does not exist"})
        if saved_profile.user != self.request.user:
            APIException.status_code = status.HTTP_401_UNAUTHORIZED
            raise APIException({
                "errors": {
                    "Unauthorized": "You are not allowed to edit this Profile"
                }
            })
        try:
            upload_info = request.data.get('avatar')
            content = request.FILES.get('avatar')
            if not content:
                APIException.status_code = status.HTTP_400_BAD_REQUEST
                raise APIException(
                    {
                        "message": "You have not supplied any file for upload"
                    })
            size = content.size
            avatar_data = str(upload_info)
            if not avatar_data.lower().endswith((".png", ".jpg", ".jpeg")):
                # checks extension of image complies with 'png','jpg' and 'jpeg' formats
                APIException.status_code = status.HTTP_400_BAD_REQUEST
                raise APIException(
                    {
                        "message": "This is an invalid avatar format, '.jpg','.jpeg', '.png' are the accepted formats"
                    })

            if size > 5021440:
                # checks that avatar size does not exceed 5mb
                APIException.status_code = status.HTTP_400_BAD_REQUEST
                raise APIException(
                    {"message": "This is image is too large, avatars cannot be more than 5mb"})

            data = {"avatar": upload_info}
            serializer = ProfileSerializer(
                instance=saved_profile, data=data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    {
                        "success": "Your profile avatar has been updated successfully"
                    }, status=200)
        except Exception as e:
            APIException.status_code = status.HTTP_400_BAD_REQUEST
            raise APIException({
                "errors": e.detail
            })
