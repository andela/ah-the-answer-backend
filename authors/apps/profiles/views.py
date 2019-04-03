from rest_framework.views import APIView
from .models import Profile
from ..authentication.models import User
from django.shortcuts import get_object_or_404
from .serializers import ProfileSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_404_NOT_FOUND, HTTP_401_UNAUTHORIZED
from django.core.exceptions import ObjectDoesNotExist
import cloudinary


class EditProfileView(APIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, username):
        """Returns a single user profile. Matches a profile
        based on the username."""
        user = User.objects.get(username=username)
        uid = user.pk
        profile = get_object_or_404(Profile.objects.all(), user_id=uid)
        serializer = ProfileSerializer(profile, many=False)
        return Response({"Profile": [serializer.data]})

    def post(self, request):
        """Creates a single user profile"""
        profile = request.data.get('profile')
        serializer = ProfileSerializer(data=profile)
        if serializer.is_valid(raise_exception=True):
            profile_saved = serializer.save(user=self.request.user)
            return Response({"Success": "Profile for '{}' created successfully"
                            .format(profile_saved.user)})
        return Response('Profile creation failed. Request contains invalid'
                        'profile data. Ensure that your JSON profile payload '
                        'contains the following fields only: user, user_bio, '
                        'name, number_of_followers, number_following and'
                        'total_article. Also ensure that the user exists.')
      
    def put(self, request, username):
        try:
            saved_profile = Profile.objects.select_related('user').get(
                user__username=username
            )
            if saved_profile.user != self.request.user:
                APIException.status_code = HTTP_401_UNAUTHORIZED
                raise APIException({
                    "errors": {
                        "Unauthorized": "You are not allowed to edit this Profile"
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
            }
        )


class AvatarView(APIView):
    permission_classes = (IsAuthenticated, )

    def patch(self, request, username):
        try:
            profile = Profile.objects.select_related('user').get(
                user__username=username
            )
        except ObjectDoesNotExist:
            APIException.status_code = HTTP_404_NOT_FOUND
            raise APIException(
                {"message": "User with that profile does not exist"})

        if saved_avatar.user != self.request.user:
            APIException.status_code = HTTP_401_UNAUTHORIZED
            raise APIException({
                "errors": {
                    "Unauthorized": "You are not allowed to edit this Profile"
                }
            })
        data = request.data.get('avatar')
        try:
            result = cloudinary.uploader.upload(
                data, allowed_formats=['png', 'jpg', 'jpeg'])
        except:
            raise ValidationError("Invalid image format")
        avatar_data = {'avatar': result['secure_url']}
        serializer = ProfileSerializer(
            instance=saved_avatar, data=avatar_data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response({"success": "Profile avatar was updated successfully"})
