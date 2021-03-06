from django.urls import path

from .views import (
    ArticleView,
    RetrieveArticleView,
    ArticleImageView,
    ArticleImageDetailView,
    LikeArticleView,
    DislikeArticleView,
    SocialShareArticleView,
    ReviewView,
    FavoriteView,
    FavoriteListView,
    HighlightView,
    UserLikesArticleView,
    AllUserLikesArticleView
)

app_name = "articles"

# app_name will help us do a reverse look-up later on.
urlpatterns = [
    path('articles/', ArticleView.as_view(), name="create-list"),
    path('articles/favorites/', FavoriteListView.as_view(),
         name="favorite-list"),
    path('articles/liked/all/', AllUserLikesArticleView.as_view(),
         name="liked-all"),
    path('articles/<slug>/', RetrieveArticleView.as_view(), name="details"),
    path('articles/<slug>/liked/', UserLikesArticleView.as_view(),
         name="liked-me"),
    path('articles/<slug>/image/', ArticleImageView.as_view(),
         name="add-image"),
    path('articles/<slug>/image/<int:id>/', ArticleImageDetailView.as_view(),
         name="image-details"),
    path('articles/<slug>/reviews/', ReviewView.as_view(), name="review"),
    path('articles/<slug>/reviews/<str:username>', ReviewView.as_view(), name="alter-review"),
    path('articles/<slug>/favorite/', FavoriteView.as_view(), name="favorite"),
    path('articles/<slug>/like/', LikeArticleView.as_view(), name="like-article"),
    path('articles/<slug>/dislike/', DislikeArticleView.as_view(), name="dislike-article"),
    path('articles/<slug>/highlight/', HighlightView.as_view(),
         name="highlight-article"),
    path("articles/<slug>/share/<provider>/",
         SocialShareArticleView.as_view(), name="share-article"),
]
