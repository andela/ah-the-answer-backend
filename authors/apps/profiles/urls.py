from django.urls import path

from .views import (AvatarView, EditProfileView,
                    CreateProfileView, RetrieveProfileView)

app_name = 'profiles'

urlpatterns = [
    path('<str:username>/avatar',
         AvatarView.as_view(), name='profile-image'),
    path('profile',
         CreateProfileView.as_view(), name='profile-create'),
    path('profiles/<str:username>',
         RetrieveProfileView.as_view(), name='profile-create'),
    path('<str:username>/edit',
         EditProfileView.as_view(), name='profile-edit'),
]
