from rest_framework import serializers
from ..bookmark.models import Bookmark


class FollowSerializer(serializers.Serializer):
    article_tiltle = serializers.CharField(max_length=100)
    article_id = serializers.IntegerField()

    def create(self, validated_data):
        return Bookmark.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.article_title = validated_data.get('article_title',
                                                    instance.article_title)
        instance.article_id = validated_data.get('article_id',
                                                 instance.article_id)
        instance.save()
        return instance