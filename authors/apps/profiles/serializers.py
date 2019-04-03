from rest_framework.serializers import ModelSerializer, ReadOnlyField, ValidationError, CharField
from .models import Profile



class ProfileSerializer(ModelSerializer):

    username = ReadOnlyField(source='get_username')
    user_id = ReadOnlyField(source='user.id')


    class Meta:
        model = Profile
        fields = ('user_id', 'username', 'user_bio', 'name',
                  'number_of_followers',
                  'number_of_followings',
                  'total_articles', 'avatar')

    def create(self, validated_data):
        return Profile.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.user_bio = validated_data.get('user_bio', instance.user_bio)
        instance.name = validated_data.get('name', instance.name)
        instance.total_articles = validated_data.get(
            'total_articles', instance.total_articles)
        instance.number_of_followings = validated_data.get(
            'number_of_followings', instance.number_of_followings)
        instance.number_of_followers = validated_data.get(
            'number_of_followers', instance.number_of_followers)
        instance.avatar = validated_data.get(
            'avatar', instance.avatar
        )

        instance.save()

        return instance
