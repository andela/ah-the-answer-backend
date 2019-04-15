from django.urls import path
from .views import (CreateRetrieveBookmark)

app_name = 'bookmark'

urlpatterns = [
    path('bookmark/<str:article_title>/', CreateRetrieveBookmark.as_view(),
         name='bookmark-create'),

]