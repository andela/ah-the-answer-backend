from django.urls import path
from .views import CommentsCreateList, CommentsDetail, CommentHistoryView


urlpatterns = [
    path(
        'articles/<slug:slug>/comments/',
        CommentsCreateList.as_view(),
        name="create-list"
    ),
    path(
        'articles/<slug:slug>/comments/<int:pk>/',
        CommentsDetail.as_view(),
        name="details"
    ),
    path(
        'articles/<slug:slug>/comments/<int:pk>/history/',
        CommentHistoryView.as_view(),
        name="comment-history"
    )
]
