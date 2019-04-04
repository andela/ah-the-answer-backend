from django.urls import path
from .views import (AvatarView, EditProfileView,
                    CreateRetrieveProfileview)

app_name = 'profiles'

urlpatterns = [
    path('<str:username>/avatar',
         AvatarView.as_view(), name='profile-avatar'),
    path('profile',
         CreateRetrieveProfileview.as_view(), name='profile-create'),
    path('profiles/<str:username>',
         CreateRetrieveProfileview.as_view(), name='profile-get'),
    path('<str:username>/edit',
         EditProfileView.as_view(), name='profile-edit'),
]
