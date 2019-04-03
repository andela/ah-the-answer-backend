from django.urls import path
from .views import (
    LoginAPIView,
    RegistrationAPIView,
    UserRetrieveUpdateAPIView,
    PasswordResetAPIView,
    SetUpdatedPasswordAPIView
)

urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view(), name="user-details"),
    path('users/', RegistrationAPIView.as_view(), name="user-signup"),
    path('users/login/', LoginAPIView.as_view(), name="user-login"),
    path('users/reset_password/', PasswordResetAPIView.as_view(), name="password-reset"),
    path('users/reset_password/<reset_token>', SetUpdatedPasswordAPIView.as_view(), name="set-updated-password")
]
