from django.urls import path
from .views import (CreateBookmark, RetrieveBookmarks)

app_name = 'bookmark'

urlpatterns = [
    path('bookmark/<str:article_title>/', CreateBookmark.as_view(),
         name='bookmark-create'),
    path('bookmarks/', RetrieveBookmarks.as_view(), name='bookmark-list'),

]