from django.urls import path
from .views import (ManageFollowers, ManageFollowings)

app_name = 'follow'

urlpatterns = [
    path('follow/<str:following>/',
         ManageFollowers.as_view(), name='follow-user'),
    path('followers/<str:user>/',
         ManageFollowers.as_view(), name='list-followers'),
    path('followings/<str:user>/',
         ManageFollowings.as_view(), name='list-followings'),
    path('unfollow/<str:user>/<str:follower>',
         ManageFollowers.as_view(), name='unfollow-user'),
]
