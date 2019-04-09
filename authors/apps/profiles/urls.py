from django.urls import path
from .views import (ProfilesListAPIview, AvatarView, EditProfileView,
                    CreateRetrieveProfileView,)

app_name = 'profiles'

urlpatterns = [
    path('profile/<str:username>/avatar/',
         AvatarView.as_view(), name='profile-image'),
    path('profile/',
         CreateRetrieveProfileView.as_view(), name='profile-create'),
    path('profiles/<str:username>/',
         CreateRetrieveProfileView.as_view(), name='profile-fetch'),
    path('profile/<str:username>/edit/',
         EditProfileView.as_view(), name='profile-edit'),
    path('profiles/', ProfilesListAPIview.as_view(), name='profiles-all')
]
