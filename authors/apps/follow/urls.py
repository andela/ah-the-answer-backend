from django.urls import path
from .views import (ManageFollows)

app_name = 'follow'

urlpatterns = [
    path('follows/<str:username>/',
         ManageFollows.as_view(), name='followers-list'),
]