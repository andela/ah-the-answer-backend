from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Article
from .serializers import ArticleSerializer


class ArticleView(APIView):
    def get(self, request):
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response({"articles": serializer.data})

    def post(self, request):
        article = request.data.get('article')

        # Create an article from the above data
        serializer = ArticleSerializer(data=article)
        if serializer.is_valid(raise_exception=True):
            article_saved = serializer.save()
        return Response({"success": "Article '{}' created successfully".format(article_saved.title)})


class RetrieveArticleView(APIView):
    def get(self, request, slug):
        try:
            article = Article.objects.get(slug=slug)
            serializer = ArticleSerializer(article, many=False)
            return Response({"article": serializer.data})
        except Article.DoesNotExist:
            return Response(
                {"message": "The article requested does not exist"}, status=404)

    def put(self, request, slug):
        saved_article = get_object_or_404(Article.objects.all(), slug=slug)
        data = request.data.get('article')
        serializer = ArticleSerializer(
            instance=saved_article, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            article_saved = serializer.save()
        return Response({"success": "Article '{}' updated successfully".format(article_saved.title)})

    def delete(self, request, slug):
        article = get_object_or_404(Article.objects.all(), slug=slug)
        article.delete()
        return Response({"message": "Article `{}` has been deleted.".format(slug)}, status=204)
