from django.urls import path

from .views import (
    CreateListReportsAPIView, GetAllReportsView
)

app_name = "reports"

urlpatterns = [
    path('report/<int:id>', CreateListReportsAPIView.as_view(), name="report-create"),
    path('reports/', GetAllReportsView.as_view(), name="fetch-reports")
]