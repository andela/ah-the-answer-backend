from django.urls import path

from .views import ArticleView, RetrieveArticleView


app_name = "articles"

# app_name will help us do a reverse look-up later on.
urlpatterns = [
    path('articles/', ArticleView.as_view()),
    path('articles/<slug>', RetrieveArticleView.as_view()),
]
