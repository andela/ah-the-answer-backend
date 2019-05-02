from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from authors.apps.articles.models import Article, LikeArticles
from authors.apps.authentication.models import User
from authors.apps.articles.serializers import LikeArticleSerializer
from django.db.models import Count

class UserArticle(APIView):

    def get(self, request, username):
        """Get the count of all articles that the user has authored"""

        permission_classes = (IsAuthenticated, )
        user = User.objects.get(username=username)
        articles = Article.objects.filter(author=user).count()

        return Response(
            {
                "articles_count":  articles
            },
            status.HTTP_200_OK
        )


class LikedArticles(APIView):
    """Get the count of all articles that the user has liked"""
    permission_classes = (IsAuthenticated, )

    def get(self, request, username):
        user = User.objects.get(username=username)
        liked = LikeArticles.objects.filter(user=user).count()
        return Response(
            {
                "likes": liked
            }, status.HTTP_200_OK)


class MostLikedArticles(APIView):
    """This view provides the top 10 most liked articles in the blog"""
    permission_classes = (IsAuthenticated,)
    serializer_class = LikeArticleSerializer

    def get(self, request):
        # return the most popular articles ranked in desc order.
        top = LikeArticles.objects.filter(likes__gt=0).order_by('-likes')\
            .values('article').annotate(total_likes=Count('likes'))

        return Response(
            {
                "popular": LikeArticleSerializer(top, many=True).data
            }, status.HTTP_200_OK)
