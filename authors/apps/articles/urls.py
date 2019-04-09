from django.urls import path

from .views import ArticleView, RetrieveArticleView, ArticleImageView, ReviewView


app_name = "articles"

# app_name will help us do a reverse look-up later on.
urlpatterns = [
    path('articles/', ArticleView.as_view(), name="create-list"),
    path('articles/<slug>/', RetrieveArticleView.as_view(), name="details"),
    path('articles/<slug>/image/', ArticleImageView.as_view(), name="add-image"),
    path('articles/<slug>/reviews/', ReviewView.as_view(), name="review")

]
