from rest_framework import serializers
from .models import Follows


class FollowingSerializer(serializers.Serializer):
    followed_user = serializers.CharField(max_length=100)
