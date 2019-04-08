from rest_framework import serializers
from .models import Follows


class FollowSerializer(serializers.Serializer):
    followed_user = serializers.CharField(max_length=100)
    following_user = models.CharField(max_length=100)
    follower_id = serializers.IntegerField()

    def create(self, validated_data):
        return Follows.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.followed_user = validated_data.get('followed_user',
                                                    instance.followed_user)
        instance.following_user = validated_data.get('following_user',
                                                     instance.following_user)
        instance.follower_id = validated_data.get('follower_id',
                                                  instance.follower_id)
        instance.save()
        return instance
