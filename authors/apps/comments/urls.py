from django.urls import path
from .views import (
    CommentsCreateList, CommentsDetail, LikeCommentView, DislikeCommentView
)

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
    path('articles/<slug:slug>/comments/<int:pk>/like/',
         LikeCommentView.as_view(),
         name="like"),
    path('articles/<slug:slug>/comments/<int:pk>/dislike/',
         DislikeCommentView.as_view(),
         name="dislike")
]
