from rest_framework.views import APIView
from .serializers import ProfileSerializer
from .models import Profile
from ..authentication.models import User
from .models import Profile
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404


class ListProfiles(APIView):
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

    def put(self, request, pk):
        saved_profile = get_object_or_404(Profile.objects.all(), pk=pk)
        data = request.data.get('profile')
        serializer = ProfileSerializer(
            instance=saved_profile, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            profile_saved = serializer.save()
        return Response({"success": "Profile '{}' updated successfully".format(profile_saved.title)})
