from django.shortcuts import render
from django.shortcuts import get_object_or_404

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

from ..authentication.models import User
from ..profiles.models import Profile
from .models import Follows

from .serializers import FollowersSerializer, FollowingSerializer


class ManageFollowers(APIView):
    """Contains views related to a user's followers. This includes methods
    that allow users to follow and unfollow each other, as well as return a
    list of all user followers. Only authenticated users may
    access the views."""
    permission_classes = (IsAuthenticated,)

    def post(self, request, following):
        """Enables one user to follower another user. The method checks if a
        user is trying to follow themselves, if the user to be followed is
        an existing user, and if the given user has already been followed."""
        follower = self.request.user.username
        if follower == following:
            return Response({'error': 'User is attempting to '
                            'follow themselves. This is not allowed.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=following).exists():
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
        """Returns a list of followers for a given user."""
        followers_list = Follows.objects.filter(followed_user=user)
        serializer = FollowersSerializer(followers_list, many=True)
        return Response({"followers": serializer.data},
                        status=status.HTTP_200_OK)

    def delete(self, request, user, follower):
        """Removes a follower from a user's following. Checks if user
        attempts to delete followers unrelated to them. It then confirms if the
        given user actually follows the given follower."""
        check_user = self.request.user.username
        if check_user != user:
            return Response({'error': 'Incorrect user logged in. '
                            'Check username in the URL.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if Follows.objects.filter(followed_user=follower).filter(
                                  following_user=user).exists():
            Follows.objects.filter(followed_user=follower).filter(
                                  following_user=user).delete()
            return Response({"success": '{} has been unfollowed.'.format(
                            follower)}, status=status.HTTP_200_OK)
        return Response({"error": 'You do not follow {}. Unfollow failed.'
                        .format(follower)}, status=status.HTTP_400_BAD_REQUEST)


class ManageFollowings(APIView):
    """Contains views related to a user's follows. This includes a method that
    returns a list of all the followed users. Only authenticated users may
    access the view."""
    permission_classes = (IsAuthenticated,)

    def get(self, request, user):
        """Returns a list of followed users for a given user."""
        followings_list = Follows.objects.filter(following_user=user)
        serializer = FollowingSerializer(followings_list, many=True)
        return Response({"followed_users": serializer.data},
                        status=status.HTTP_400_BAD_REQUEST)


class UserStats(APIView):
    """Contains views related to calculating statistics based on a user's
    followers and follows. This includes a method that counts the number of
    followers and follows of a given user."""
    def get(self, request, user):
        """Returns a count of a user's followers and follows."""
        user_profile = Profile.objects.get(user__username=user)
        if not User.objects.filter(username=user).exists():
            return Response({"error": "This given username does not have an "
                            "Author's Haven account."},
                            status=status.HTTP_400_BAD_REQUEST)
        amount_followings = Follows.objects.filter(
                              following_user=user).count()
        amount_followers = Follows.objects.filter(
                            followed_user=user).count()
        user_profile.number_of_followings = amount_followings
        user_profile.number_of_followers = amount_followers
        user_profile.save()
        return Response({"success": [{"follows": amount_followings},
                        {"followers": amount_followers}]},
                        status=status.HTTP_200_OK)
