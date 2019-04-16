from django.urls import path
from .views import (CreateRetrieveBookmark, RetrieveBookmarks)

app_name = 'bookmark'

urlpatterns = [
    path('bookmark/<str:article_title>/', CreateRetrieveBookmark.as_view(),
         name='bookmark-create'),
    path('bookmarks/', RetrieveBookmarks.as_view(), name='bookmark-list'),

]