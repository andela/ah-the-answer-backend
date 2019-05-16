from rest_framework import serializers
from .models import (Article, ArticleImage, FavoriteModel, ReviewsModel,
                     LikeArticles, Highlight)
from ..authentication.serializers import UserSerializer
from django.core.validators import MaxValueValidator, MinValueValidator
from taggit_serializer.serializers import (
    TagListSerializerField,
    TaggitSerializer
    )

class TagSerializer(TagListSerializerField):
    """
    Class defines error messages for tags list
    """
    default_error_messages = {
        'not_a_list': '"{input_type}" provided in the '
            'tags field is not a list.',
        'not_a_str': 'items in the tags list must be of string type',
        'invalid_json': 'tags field must be a list containing tags'
    }

class ArticleSerializer(TaggitSerializer, serializers.ModelSerializer):
    """Serializer to map the Article Model instance into JSON format."""

    author = UserSerializer(read_only=True)
    title = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=128)
    body = serializers.CharField()
    tags = TagSerializer()
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()

    def create(self, validated_data):
        article = Article.objects.create(**validated_data)
        tagged_article = Article.objects.get(pk=article.pk)
        for tag in article.tags:
            tagged_article.tags.add(tag)
        return article
        
    def update(self, instance, validated_data):
        tag_list = validated_data.pop('tags', instance.tags.all())
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.body = validated_data.get('body', instance.body)
        instance.is_published = validated_data.get(
            'is_published', instance.is_published)
        instance.tags.set(*tag_list)
        instance.save()
        return instance

    def get_like_count(self, obj):
        """method returns number of likes for an article"""
        return obj.liked.filter(likes=1).count()

    def get_dislike_count(self, obj):
        """method returns the sum of dislikes for an article"""
        return obj.liked.filter(likes=0).count()

    class Meta:
        model = Article
        fields = ('id', 'title', 'body', 'description', 'is_published',
                  'date_created', 'date_modified', 'slug', 'read_time', 'author',
                  'like_count', 'dislike_count', 'tags')
        read_only_fields = ('date_created', 'date_modified', 'slug', 'read_time', 'author')


class ArticleImageSerializer(serializers.ModelSerializer):
    """Serializer to map the Article Image Model metadata into JSON format."""
    article = serializers.ReadOnlyField(source='article.id')
    image_url = serializers.CharField()

    def create(self, validated_data):
        return ArticleImage.objects.create(**validated_data)

    class Meta:
        model = ArticleImage
        fields = "__all__"
        read_only_fields = ["date_created"]


class ReviewsSerializer(serializers.ModelSerializer):
    rating_value = serializers.IntegerField(validators=[MaxValueValidator(5),
                                                   MinValueValidator(0)])
    reviewer_username = serializers.ReadOnlyField(
        source='reviewed_by.username')
    article = serializers.ReadOnlyField(source='article.pk')
    avg_rating = serializers.ReadOnlyField(source='average_rating(article)')

    class Meta:
        model = ReviewsModel
        fields = '__all__'

        read_only_fields = ('average_rating', 'date_created', 'date_modified',
                            'article', 'reviewed_by', 'reviewer_username', 'avg_rating')


    def update(self, instance, validated_data):

        instance.review_body = validated_data.get(
            'review_body', instance.review_body)
        instance.rating_value = validated_data.get(
            'rating_value', instance.rating_value)

        instance.save()

        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    article = ArticleSerializer()
    user = UserSerializer()

    class Meta:
        model = FavoriteModel
        fields = '__all__'
        read_only_fields = ['date_modified', 'date_created']


class CommentInlineSerializer(serializers.ModelSerializer):

    class Meta:
        model = Article
        fields = ('slug', )


class HighlightSerializer(serializers.ModelSerializer):
    """Serializer to map the Highlight Model instance into JSON format."""
    article = serializers.ReadOnlyField(source='article.id')
    user = UserSerializer(read_only=True)

    class Meta:
        model = Highlight
        fields = ('id', 'user', 'article', 'start', 'end',
                  'section', 'date_created', 'comment')
        read_only_fields = ['date_created', 'section']

class ArticleField(serializers.RelatedField):
    queryset = Article.objects.all()

    def to_representation(self, pk):
        return ArticleSerializer(self.queryset.get(pk=pk)).data


class LikeArticleSerializer(serializers.ModelSerializer):
    """Serializer the LikeArticlesModel"""
    total_likes = serializers.CharField()
    article = ArticleField()

    class Meta:
        model = LikeArticles
        fields = ['article', 'total_likes']
        depth = 1


class UserLikesArticleSerialzer(serializers.ModelSerializer):
    """This serializer is used to determine whether a user has already liked
    an articles"""
    class Meta:
        model = LikeArticles
        fields = ['article','likes']