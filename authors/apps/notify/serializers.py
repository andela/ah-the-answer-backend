from rest_framework import serializers
from authors.apps.notify.models import Notification
from authors.apps.authentication.serializers import UserSerializer


class NotificationSerializer(serializers.ModelSerializer):
    body = serializers.CharField()
    recepient = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = ['id', 'createdAt', 'body', 'recepient']
        read_only = ['id', 'createdAt', 'recepient']
