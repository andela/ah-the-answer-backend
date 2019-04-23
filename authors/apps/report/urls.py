from django.urls import path

from .views import (
    CreateListReportsAPIView
)

app_name = "reports"

urlpatterns = [
    path('report/', CreateListReportsAPIView.as_view(),
         name="report-create")
]