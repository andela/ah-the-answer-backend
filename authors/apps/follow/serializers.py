from rest_framework import serializers
from .models import Follows


class FollowersSerializer(serializers.Serializer):
    #followed_user = serializers.CharField(max_length=100)
    following_user = serializers.CharField(max_length=100)
    #follower_id = serializers.IntegerField()


class FollowingSerializer(serializers.Serializer):
    followed_user = serializers.CharField(max_length=100)
    

    