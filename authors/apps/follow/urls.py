from django.urls import path
from .views import (ManageFollowers, ManageFollowings, UserStats, CheckFollow)

app_name = 'follow'

urlpatterns = [
    path('follow/<str:user_to_follow>/',
         ManageFollowers.as_view(), name='follow-user'),
    path('checkfollow/<str:user_to_follow>/',
         CheckFollow.as_view(), name='check-follow'),
    path('followers/',
         ManageFollowers.as_view(), name='list-followers'),
    path('followings/',
         ManageFollowings.as_view(), name='list-followings'),
    path('unfollow/<str:followed_user>/',
         ManageFollowers.as_view(), name='unfollow-user'),
    path('follows/count/<str:user>/',
         UserStats.as_view(), name='count-follows')
]
