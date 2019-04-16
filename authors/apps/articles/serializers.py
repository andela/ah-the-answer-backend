from rest_framework import serializers
from .models import Article, ArticleImage
from ..authentication.serializers import UserSerializer

class TagSerializer(serializers.Field):
    """serializer for the tag field"""
    def to_internal_value(self, data):
        tag_data = ArticleSerializer().validate_tags(data)
        return tag_data
    
    def to_representation(self, obj):
        if type(obj) is not list:
            return [tag for tag in obj.all()]
        return obj

class ArticleSerializer(serializers.ModelSerializer):
    """Serializer to map the Article Model instance into JSON format."""

    author = UserSerializer(read_only=True)
    title = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=128)
    body = serializers.CharField()
    tags = TagSerializer(default=[], required=False)
    like_count = serializers.SerializerMethodField()
    dislike_count = serializers.SerializerMethodField()

    def validate_tags(self, validated_data):
        if type(validated_data) is not list:
            raise serializers.ValidationError(
                {"message": "tags should be in a list"}
            )
        for tag in validated_data:
            if not isinstance(tag, str):
                raise serializers.ValidationError(
                    {"message": "tag should be a string"}
                )
            return validated_data

    def create(self, validated_data):
        article = Article.objects.create(**validated_data)
        tagged_article = Article.objects.get(pk=article.pk)
        if article.tags is not None:
            for tag in article.tags:
                tagged_article.tags.add(tag)
            return article
        article.tags = []
        return article

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.body = validated_data.get('body', instance.body)
        instance.is_published = validated_data.get('is_published', instance.is_published)
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
    image = serializers.CharField()

    def create(self, validated_data):
        return ArticleImage.objects.create(**validated_data)

    class Meta:
        model = ArticleImage
        fields = "__all__"
        read_only_fields = ["date_created"]
