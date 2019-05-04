from django.urls import path
from authors.apps.stats.views import (
    UserArticle, LikedArticles, MostLikedArticles
)

urlpatterns = [
    path(
        'stats/popular/',
        MostLikedArticles.as_view(),
        name='popular-articles'
    ),
    path(
        'stats/<username>/likes/',
        LikedArticles.as_view(),
        name="liked-articles"
    ),
    path(
        'stats/<username>/articles/',
        UserArticle.as_view(),
        name="user-articles"
    )
]
