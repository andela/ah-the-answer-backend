from rest_framework import serializers
from .models import Article, ArticleImage, FavoriteModel
from ..authentication.serializers import UserSerializer


class ArticleSerializer(serializers.ModelSerializer):
    """Serializer to map the Article Model instance into JSON format."""

    author = UserSerializer(read_only=True)
    title = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=128)
    body = serializers.CharField()

    def create(self, validated_data):
        return Article.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get(
            'description', instance.description)
        instance.body = validated_data.get('body', instance.body)
        instance.is_published = validated_data.get('is_published', instance.is_published)
        instance.save()
        return instance

    class Meta:
        model = Article
        fields = ('id', 'title', 'body', 'description', 'is_published',
                  'date_created', 'date_modified', 'slug', 'read_time', 'author')
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


class FavoriteSerializer(serializers.ModelSerializer):
    article = ArticleSerializer()
    user = UserSerializer()

    class Meta:
        model = FavoriteModel
        fields = '__all__'
        read_only_fields = ['date_modified', 'date_created']