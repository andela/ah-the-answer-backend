from rest_framework import serializers
from .models import Follows


class FollowersSerializer(serializers.Serializer):
    follower = serializers.CharField(max_length=100)


class FollowingSerializer(serializers.Serializer):
    followed_user = serializers.CharField(max_length=100)
