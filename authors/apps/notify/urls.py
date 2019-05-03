from django.urls import path
from authors.apps.notify.views import (
    NotificationsAPIView,
    NotificationsDetailAPIView,
    NotificationsUnsubscribe,
    NotificationRead,
    NotificationsAll,
    NotificationReadUnread
)


urlpatterns = [
    path(
        'notifications/',
        NotificationsAPIView.as_view(),
        name='all-notifications'
    ),
    path(
        'notifications/subscription',
        NotificationsUnsubscribe.as_view(),
        name='subscription'
    ),
    path(
        'notifications/<int:id>/',
        NotificationsDetailAPIView.as_view(),
        name='detail-notification'
    ),
    path(
        'notifications/<int:id>/state',
        NotificationRead.as_view(),
        name='state-notification'
    ),
    path(
        'notifications/read-all',
        NotificationsAll.as_view(),
        name='read-all-notifications'
    ),
    path(
        'notifications/<str:action>/',
        NotificationReadUnread.as_view(),
        name='read-unread-notifications'
    )
]
