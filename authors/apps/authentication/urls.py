from django.urls import path
from .views import (
    LoginAPIView, RegistrationAPIView,
    UserRetrieveUpdateAPIView,
    EmailVerificationView,
    PasswordResetAPIView,
    SetUpdatedPasswordAPIView,
    GoogleAuthView,
    FacebookAuthAPIView,
    TwitterAuthAPIView,
    SetUpdatedPasswordAPIView


)

urlpatterns = [
    path('user/', UserRetrieveUpdateAPIView.as_view(), name="user-details"),
    path('users/', RegistrationAPIView.as_view(), name="user-signup"),
    path('users/login/', LoginAPIView.as_view(), name="user-login"),
    path('activate/<str:token>', EmailVerificationView.as_view(), name='email verification'),
    path('users/reset_password/', PasswordResetAPIView.as_view(), name="password-reset"),
    path('users/reset_password/<reset_token>/', SetUpdatedPasswordAPIView.as_view(), name="set-updated-password"),
    path('users/google/', GoogleAuthView.as_view(), name="google"),
    path('users/facebook/', FacebookAuthAPIView.as_view(), name="facebook"),
    path('users/twitter/', TwitterAuthAPIView.as_view(), name="twitter"),

]
