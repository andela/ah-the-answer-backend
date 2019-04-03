from django.urls import path
from .views import (AvatarView, EditProfileView,
                    CreateRetrieveProfileView)
                    
app_name = 'profiles'

urlpatterns = [
    path('v1/profile/<str:username>/avatar/',
         AvatarView.as_view(), name='profile-image'),
    path('v1/profile/',
         CreateRetrieveProfileView.as_view(), name='profile-create'),
    path('v1/profiles/<str:username>',
         CreateRetrieveProfileView.as_view(), name='profile-fetch'),
    path('v1/profile/<str:username>/edit/',
         EditProfileView.as_view(), name='profile-edit'),
]
