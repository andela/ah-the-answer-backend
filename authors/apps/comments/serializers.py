from rest_framework import serializers, exceptions
from authors.apps.comments.models import Comment
from authors.apps.authentication.serializers import UserSerializer
from authors.apps.profiles.serializers import ProfileSerializer
from authors.apps.articles.serializers import ArticleSerializer


class CommentSerializer(serializers.ModelSerializer):
    body = serializers.CharField()
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'createdAt', 'updatedAt', 'body', 'author']
        read_only = ['id', 'createdAt', 'updatedAt', 'author']
