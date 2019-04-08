from django.shortcuts import render
from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from ..authentication.models import User
from .models import Follows

from .serializers import FollowSerializer


class ManageFollows(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, following):
        """Enables one user to follower another user. The method checks if a
        user is trying to follow themselves, if the user to be followed is
        an existing user, and finally if the user has already been followed."""
        follower = self.request.user.username
        if follower == following:
            return Response({'error': 'User is attempting to '
                            'follow themselves. This is not allowed.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if User.objects.get(username=following).exists():
                if Follows.objects.filter(followed_user=following).filter(following_user=follower).exists():
                    return Response({'error': 'User already followed.'},
                                    status=status.HTTP_400_BAD_REQUEST)
                follow = Follows(followed_user=following,
                                 following_user=follower,
                                 follower=self.request.user)
                follow.save()
                return Response({'success': 'Now following {}.'.format(
                                following)}, status=status.HTTP_201_CREATED)
        return Response({'error': 'Unable to create a following. '
                        'This user does not exist. Please choose another '
                         'user.'}, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request, user):
        followers_list = Follows.objects.filter(followed_user=user)
        serializer = FollowSerializer(followers_list, many=True)
        return Response({"followers": serializer.data})
