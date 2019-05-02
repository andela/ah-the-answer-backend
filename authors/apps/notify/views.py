import os
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from authors.apps.notify.models import Notification
from authors.apps.notify.serializers import NotificationSerializer
from authors.apps.authentication.models import User
from authors.apps.articles.models import Article
from authors.apps.profiles.models import Profile
from authors.apps.follow.models import Follows
from authors.apps.articles.models import FavoriteModel
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import *


class NotificationsAPIView(APIView):
    """
    Retrieves all the notifications for the currently logged in user
    """

    permission_classes = (IsAuthenticated, )

    def get(self, request):
        all_notifs = Notification.objects.filter(recepient=self.request.user)
        serializer = NotificationSerializer(all_notifs, many=True)

        return Response(
            {
                "notifications": serializer.data
            }
        )


class NotificationsUnsubscribe(APIView):
    """
    Allows users to subscribe or unsubscribe from email
    notifications
    """
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = User.objects.get(username=self.request.user.username)

        return Response(
            {
                "subscription": {
                    "status": user.is_subscribed
                }
            },
            status.HTTP_200_OK
        )

    def post(self, request):
        user = User.objects.get(username=self.request.user.username)
        user.is_subscribed = not user.is_subscribed
        user.save()

        if user.is_subscribed:
            message = "You have subscribed to email notifications"
        else:
            message = "You have unsubscribed to email notifications"

        return Response(
            {
                "success": message
            },
            status.HTTP_200_OK
        )


class NotificationsDetailAPIView(APIView):
    """
    Retrieves a specific notification
    """

    permission_classes = (IsAuthenticated, )

    def get(self, request, id):
        try:
            one_notif = Notification.objects.get(
                pk=id,
                recepient=self.request.user
            )
            serializer = NotificationSerializer(one_notif)

            return Response(
                {
                    "notifications": serializer.data
                },
                status.HTTP_200_OK
            )
        except ObjectDoesNotExist:
            return Response(
                {
                    "notifications": {
                        "error": "The record does not exist"
                    }
                },
                status.HTTP_404_NOT_FOUND
            )


class NotificationReadUnread(APIView):
    """
    Retrieve the read or unread notifications
    """

    permission_classes = (IsAuthenticated, )

    def get(self, request, action):
        state = False

        if action == 'read':
            state = True
        elif action == 'unread':
            state = False
        else:
            return Response(
                {
                    "error": "The URL action only allows 'read' and 'unread'"
                },
                status.HTTP_404_NOT_FOUND
            )

        all_notifs = Notification.objects.filter(
            is_read=state,
            recepient=self.request.user
        )

        serializer = NotificationSerializer(all_notifs, many=True)

        return Response(
            {
                "notifications": serializer.data
            },
            status.HTTP_200_OK
        )


class NotificationRead(APIView):
    """
    Marks a specific notification as read
    """

    permission_classes = (IsAuthenticated, )

    def get(self, request, id):
        try:
            notif = Notification.objects.get(pk=id)
            serializer = NotificationSerializer(notif)

            return Response(
                {
                    "is_read": notif.is_read,
                    "notification": serializer.data
                },
                status.HTTP_200_OK
            )
        except ObjectDoesNotExist:
            return Response(
                {
                    "notifications": {
                        "error": "The record does not exist"
                    }
                },
                status.HTTP_404_NOT_FOUND
            )

    def put(self, request, id):
        try:
            notif = Notification.objects.get(pk=id)
            notif.is_read = not notif.is_read
            notif.save()

            serializer = NotificationSerializer(notif)

            if notif.is_read:
                m = 'READ'
            else:
                m = 'UNREAD'

            return Response(
                {
                    "success": "Notification has been marked as '{0}' ".format(
                        m
                    ),
                    "notifications": serializer.data
                },
                status.HTTP_200_OK
            )
        except ObjectDoesNotExist:
            return Response(
                {
                    "notifications": {
                        "error": "The record does not exist"
                    }
                },
                status.HTTP_404_NOT_FOUND
            )


class NotificationsAll(APIView):
    """
    Marks all the notifications for the currently logged in user as 'READ'
    """

    permission_classes = (IsAuthenticated, )

    def put(self, request):
        all_notifs = Notification.objects.filter(recepient=self.request.user)

        for notif in all_notifs:
            notif.is_read = True
            notif.save()

        return Response(
            {
                "success": "All notifications have been marked as 'READ' "
            }
        )

    def delete(self, request):
        all_notifs = Notification.objects.filter(
            recepient=self.request.user,
            is_read=True
        ).delete()

        return Response(
            {
                "success": "All read notifications have been Deleted "
            }
        )


class NotificationsView():

    @classmethod
    def get_recepients(cls, instance, _type):
        """
        Get the users who should receive the notification
        """
        user_email = instance.get('author').get('email')
        user = User.objects.get(email=user_email)
        recepients = []

        if _type == 'new-article':
            qs = Follows.objects.filter(
                followed_user=user.username
            )
            for item in qs:
                recepients.append(item.follower.email)

        elif _type == 'new-comment':
            comment_article = Article.objects.get(
                slug=instance.get('article').get('slug')
            )
            qs = FavoriteModel.objects.filter(
                article=comment_article
            )

            for item in qs:
                recepients.append(item.user.email)

        return recepients

    @classmethod
    def send_notification(cls, message, instance, _type):
        """
        Sends notifications to users and updates the notifications table
        """
        recepients = cls.get_recepients(instance, _type)

        for user_email in recepients:
            Notification.objects.create(
                body=message,
                recepient=User.objects.get(email=user_email)
            )

            cls.send_email(user_email, message)

        return

    @classmethod
    def send_email(cls, user_email, message):
        """
        Sends an email notification to users
        """
        sg = SendGridAPIClient(apikey=os.getenv('SENDGRID_API_KEY'))
        to_email = Email(email=user_email)
        from_email = Email(email=os.getenv('FROM_EMAIL'))
        user = User.objects.get(email=user_email)

        if user.is_subscribed:
            subject = 'Authors Haven'
            content = Content("text/plain", message)

            try:
                mail = Mail(from_email, subject, to_email, content)
                response = sg.client.mail.send.post(request_body=mail.get())
                cls.count += 1
                if response.status_code is not 202:
                    return "check sender email and API key settings"
                return "Email sent to {}".format(user_email)
            except Exception:
                return "Error while sending mail to provided account"
