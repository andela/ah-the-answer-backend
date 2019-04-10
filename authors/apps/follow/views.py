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

    def post(self, request, user_to_follow):
        """Enables one user to follower another user. The method checks if a
        user is trying to follow themselves. It also checks if the user to be
        followed is an existing user, as well as if they have already been
        followed."""
        check_user = self.request.user
        if check_user.username == user_to_follow:
            return Response({'error': 'User is attempting to '
                            'follow themselves. This is not allowed.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if not User.objects.filter(username=user_to_follow).exists():
                return Response({'error': 'Unable to create a following. '
                                 'This user does not exist. Please '
                                 'choose another user.'},
                                status=status.HTTP_400_BAD_REQUEST)
        if Follows.objects.filter(followed_user=user_to_follow).filter(
                                 follower_id=check_user.pk).exists():
                return Response({'error': 'User already followed.'},
                                status=status.HTTP_400_BAD_REQUEST)
        new_follow = Follows(followed_user=user_to_follow,
                             follower=check_user)
        new_follow.save()
        return Response({'success': 'Now following {}.'.format(
                        user_to_follow)}, status=status.HTTP_201_CREATED)

    def get(self, request, user):
        """Returns a list of followers for a given user."""
        follower_list = Follows.objects.filter(followed_user=user)
        queries = [i.follower.username for i in follower_list]
        return Response({"followers": queries},
                        status=status.HTTP_200_OK)

    def delete(self, request, user, followed_user):
        """Removes a previously followed user from a user's list of followers.
        Checks if user attempts to delete followers unrelated to them. It then
        confirms if the given user actually follows the given follower."""
        check_user = self.request.user
        if check_user.username != user:
            return Response({'error': 'Incorrect user logged in. '
                            'Check username in the URL.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if not Follows.objects.filter(followed_user=followed_user).filter(
                                     follower_id=check_user.pk).exists():
            return Response({"error": 'You do not follow {}. Unfollow failed.'
                            .format(followed_user)},
                            status=status.HTTP_400_BAD_REQUEST)
        Follows.objects.filter(followed_user=followed_user).filter(
                               follower_id=check_user.pk).delete()
        return Response({"success": '{} has been unfollowed.'.format(
                        followed_user)}, status=status.HTTP_200_OK)


class ManageFollowings(APIView):
    """Contains views related to a user's follows. This includes a method that
    returns a list of all the followed users. Only authenticated users may
    access the view."""
    permission_classes = (IsAuthenticated,)

    def get(self, request, user):
        """Returns a list of other users that the current user follows."""
        check_user = self.request.user
        followed_users_list = Follows.objects.filter(follower_id=check_user.pk)
        serializer = FollowingSerializer(followed_users_list, many=True)
        return Response({"followed_users": serializer.data},
                        status=status.HTTP_400_BAD_REQUEST)


class UserStats(APIView):
    """Contains views related to calculating statistics based on a user's
    followers and follows. This includes a method that counts the number of
    followers and follows of a given user."""
    def get(self, request, user):
        """Returns a count of a user's followers and follows."""
        try:
            check_user = User.objects.get(username=user)
        except:
            return Response({"error": "This given username does not have an "
                            "Author's Haven account."},
                            status=status.HTTP_400_BAD_REQUEST)
        user_profile = Profile.objects.get(user__username=user)
        number_users_followed = Follows.objects.filter(
                              follower_id=check_user.pk).count()
        number_of_followers = Follows.objects.filter(
                            followed_user=user).count()
        user_profile.number_of_followings = number_users_followed
        user_profile.number_of_followers = number_of_followers
        user_profile.save()
        return Response({"success": [{"follows": number_users_followed},
                        {"followers": number_of_followers}]},
                        status=status.HTTP_200_OK)
