from rest_framework.serializers import ModelSerializer, ReadOnlyField
from .models import Profile


class ImageSerializer(ModelSerializer):

    class Meta:
        model = Record
        fields = ('avatar',)

    def update(self, instance, validated_data):
        instance.image = validated_data.get('avatar', instance.image)
        instance.save()

        return instance


class ProfileSerializer(ModelSerializer):

    #username = ReadOnlyField(source='get_username')
    #image_url = ReadOnlyField(source='cloudinary_image_url')

    class Meta:
        model = Profile
        fields = '__all__'

    def create(self, validated_data):
        return Profile.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.user_bio = validated_data.get('user_bio', instance.user_bio)
        instance.name = validated_data.get('name', instance.name)
        instance.total_articles = validated_data.get('total_articles', instance.total_articles)
        instance.number_of_following = validated_data.get('number_of_following', instance.number_of_following)
        instance.number_of_followers = validated_data.get('number_of_followers', instance.number_of_followers)

        instance.save()

        return instance

