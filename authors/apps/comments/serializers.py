from rest_framework import serializers, exceptions
from authors.apps.comments.models import Comment
from authors.apps.authentication.serializers import UserSerializer
from authors.apps.profiles.serializers import ProfileSerializer
from authors.apps.articles.serializers import (
    ArticleSerializer, CommentInlineSerializer
)


class CommentHistoryField(serializers.ListField):
    child = serializers.DictField()

    def to_representation(self, data):
        return super().to_representation(data.values())


class CommentSerializer(serializers.ModelSerializer):
    body = serializers.CharField()
    author = UserSerializer(read_only=True)
    article = CommentInlineSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'createdAt', 'updatedAt', 'body', 'article', 'author']
        read_only = ['id', 'createdAt', 'updatedAt', 'article', 'author']


class CommentHistorySerializer(serializers.ModelSerializer):
    # body = serializers.CharField()
    comment_history = CommentHistoryField(read_only=True)

    class Meta:
        model = Comment
        fields = ['comment_history']
        read_only = ['comment_history']
