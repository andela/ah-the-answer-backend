from django.urls import path


from .views import ListProfiles
app_name = "profiles"


urlpatterns = [
    path('v1/profiles/', ListProfiles.as_view()),
    path('v1/profiles/<str:username>/', ListProfiles.as_view()),
]