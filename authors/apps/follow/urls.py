from django.urls import path
from .views import (ManageFollows)

app_name = 'follow'

urlpatterns = [
    path('follow/<str:following>/',
         ManageFollows.as_view(), name='follow-user'),
    path('followers/<str:user>/',
         ManageFollows.as_view(), name='list-followers')
]