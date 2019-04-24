from django.urls import path
from .views import (CreateBookmark, RetrieveBookmarks)

app_name = 'bookmark'

urlpatterns = [
    path('bookmark/<int:article_id>/', CreateBookmark.as_view(),
         name='bookmark-create'),
    path('bookmarks/', RetrieveBookmarks.as_view(), name='bookmark-list'),

]