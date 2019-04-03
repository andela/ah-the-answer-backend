from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import Article, ArticleImage
from .serializers import ArticleSerializer, ArticleImageSerializer
from .permissions import ReadOnly
from authors.apps.authentication.models import User
import cloudinary


class ArticleView(APIView):
    permission_classes = (IsAuthenticated | ReadOnly,)

    def get(self, request):
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response({"articles": serializer.data})

    def post(self, request):
        article = request.data.get('article')

        # Create an article from the above data
        serializer = ArticleSerializer(data=article)
        if serializer.is_valid(raise_exception=True):
            article_saved = serializer.save(author=self.request.user)

        return Response(
            {
                "success": "Article '{}' created successfully".format(article_saved.title)
            }, status=201)


class RetrieveArticleView(APIView):
    permission_classes = (IsAuthenticated | ReadOnly,)

    def is_owner(self, current_user_id, article_author_id):
        if article_author_id == current_user_id:
            return True
        return False

    def get(self, request, slug):
        try:
            article = Article.objects.get(slug=slug)
            serializer = ArticleSerializer(article, many=False)
            return Response({"article": serializer.data})
        except Article.DoesNotExist:
            return Response(
                {"message": "The article requested does not exist"}, status=404)

    def put(self, request, slug):
        try:
            saved_article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            return Response(
                {"message": "The article requested does not exist"}, status=404)

        data = request.data.get('article')
        serializer = ArticleSerializer(
            instance=saved_article, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            if self.is_owner(saved_article.author.id, request.user.id) is True:
                article_saved = serializer.save()
                return Response({"success": "Article '{}' updated successfully".format(article_saved.title)})
            response = {"message": "Only the owner can edit this article."}
            return Response(response, status=401)

    def delete(self, request, slug):
        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            return Response(
                {"message": "The article requested does not exist"}, status=404)

        if self.is_owner(article.author.id, request.user.id) is True:
            article.delete()
            return Response({"message": "Article `{}` has been deleted.".format(slug)}, status=200)

        response = {"message": "Only the owner can delete this article."}
        return Response(response, status=401)


class ArticleImageView(APIView):
    permission_classes = (IsAuthenticated | ReadOnly,)

    def post(self, request, slug):

        try:
            article = Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            return Response(
                {"message": "The article requested does not exist"}, status=404)

        if request.FILES:
            response = cloudinary.uploader.upload(request.FILES['file'])
            image_url = response.get('secure_url')

            serializer = ArticleImageSerializer(data={"image": image_url})
            if serializer.is_valid(raise_exception=True):
                image_saved = serializer.save(article=article)

            response = {"message": "Image uploaded Successfully"}
            return Response(response, status=200)

        else:
            response = {"message": "Image uploaded failed."}
            return Response(response, status=400)

    def get(self, request, slug):
        images = ArticleImage.objects.select_related('article').filter(article__slug=slug)
        serializer = ArticleImageSerializer(images, many=True)
        return Response({"images": serializer.data})
