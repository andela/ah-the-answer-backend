from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException

from rest_framework import status

from django.db.models import Q


from .models import Article, ArticleImage, LikeArticles
from .serializers import ArticleSerializer, ArticleImageSerializer
from .permissions import ReadOnly
from authors.apps.authentication.models import User
from .filters import ArticleFilter
import cloudinary

def find_article(slug):
    """Method to check if an article exists"""
    try:
        return Article.objects.get(slug=slug)
    except Article.DoesNotExist:
        APIException.status_code = 404
        raise APIException({
            "message": "The article requested does not exist"
        })

class ArticleView(APIView):
    """Class that contains the method that retrieves all articles and creates an article"""
    permission_classes = (IsAuthenticated | ReadOnly,)
    filter_fields = ('author', 'title',)

    def get(self, request):
        """Method to get all articles"""
        # Functionality to search articles by description, author and title
        if request.GET.get('search'):
            search_parameter = request.GET.get('search')

            searched_articles = Article.objects.filter(Q(
                title__icontains=search_parameter) | Q(description__icontains=search_parameter) | Q(author__username__icontains=search_parameter))
            # filter the model for tags by converting query parameters into a list and 
            # comparing that query list with list of tags in every instance of the object
            if not searched_articles:
                tag_list = search_parameter.split(",")
                searched_articles = Article.objects.filter(
                    tags__name__in=tag_list
                )
                searched_articles.distinct()
            search_serializer = ArticleSerializer(
                searched_articles, many=True)
            return Response({"articles": search_serializer.data})

        # Functionality to filter articles by author and title
        articles = Article.objects.all()
        article_filter = ArticleFilter()
        filtered_articles = article_filter.filter_queryset(
            request, articles, self)
        if filtered_articles.exists():
            for article in filtered_articles:
                article.tags = list(article.tags.names())
            serializer = ArticleSerializer(filtered_articles, many=True)
            return Response({"articles": serializer.data}, status=200)
        else:
            return Response({"message":"No article found","articles": []}, status=200)

    def post(self, request):
        """Method to create an article"""
        article = request.data.get('article')

        # Create an article from the above data
        serializer = ArticleSerializer(data=article)
        if serializer.is_valid(raise_exception=True):
            article_saved = serializer.save(author=self.request.user)

        return Response({
            "success": "Article '{}' created successfully".format(article_saved.title),
            "article": serializer.data
        }, status=201)


class RetrieveArticleView(APIView):
    """Class with get, put and delete methods"""
    permission_classes = (IsAuthenticated | ReadOnly,)

    def is_owner(self, current_user_id, article_author_id):
        if article_author_id == current_user_id:
            return True

    def get(self, request, slug):
        """Method to get a specific article"""
        article = find_article(slug)
        article.tags = list(article.tags.names())
        serializer = ArticleSerializer(article, many=False)
        return Response({"article": serializer.data})

    def put(self, request, slug):
        """Method to update a specific article"""
        saved_article = find_article(slug)
        data = request.data.get('article')
        serializer = ArticleSerializer(
            instance=saved_article, data=data, partial=True)
        if serializer.is_valid(raise_exception=True):
            if self.is_owner(saved_article.author.id, request.user.id) is True:
                article_saved = serializer.save()
                return Response({
                    "success": "Article '{}' updated successfully".format(article_saved.title),
                    "article": serializer.data
                })
            response = {"message": "Only the owner can edit this article."}
            return Response(response, status=403)

    def delete(self, request, slug):
        """Method to delete a specific article"""
        article = find_article(slug)

        if self.is_owner(article.author.id, request.user.id) is True:
            article.delete()
            return Response({"message": "Article `{}` has been deleted.".format(slug)}, status=200)

        response = {"message": "Only the owner can delete this article."}
        return Response(response, status=403)


class ArticleImageView(APIView):
    """Class with methods to upload an image and retrieve all images of an article"""
    permission_classes = (IsAuthenticated | ReadOnly,)

    def post(self, request, slug):
        """Method to upload an image"""
        article = find_article(slug)

        if request.FILES:
            try:
                response = cloudinary.uploader.upload(
                    request.FILES['file'], allowed_formats=['png', 'jpg', 'jpeg'])
            except Exception as e:
                APIException.status_code = 400
                raise APIException({
                    "errors": str(e)
                })
            image_url = response.get('secure_url')

            serializer = ArticleImageSerializer(data={"image": image_url})
            if serializer.is_valid(raise_exception=True):
                serializer.save(article=article)

            response = {"message": "Image uploaded Successfully"}
            return Response(response, status=200)

        else:
            response = {"message": "Image uploaded failed."}
            return Response(response, status=400)

    def get(self, request, slug):
        """Method to get all images of an article"""
        find_article(slug)
        images = ArticleImage.objects.select_related(
            'article').filter(article__slug=slug)
        serializer = ArticleImageSerializer(images, many=True)
        return Response({"images": serializer.data})

class LikeArticleView(APIView):
    """
    Class for POST view allowing authenticated users to like articles
    """
    permission_classes = (IsAuthenticated,)
    def post(self, request, slug):
        """
        method for generating a like for a particular article
        """
        article = find_article(slug)
        liked = LikeArticles.react_to_article(request.user, article, 1)
        if not liked:
            return Response({
                'message': 'you have reverted your' \
                    ' like for the article: {}'.format(article.title),
                'article': ArticleSerializer(article).data  
            }, status=status.HTTP_202_ACCEPTED)
        return Response({
            'message': 'you liked the article: {}'.format(article.title),
            'article': ArticleSerializer(article).data
        },
        status=status.HTTP_201_CREATED)

class DislikeArticleView(APIView):
    """
    Class for POST view allowing authenticated users to dislike articles
    """
    permission_classes = (IsAuthenticated,)
    def post(self, request, slug):
        """
        method for generating a dislike for a particular article
        """
        article = find_article(slug)
        disliked = LikeArticles.react_to_article(request.user, article, 0)
        if not disliked:
            return Response({
                'message': 'you have reverted your' \
                    ' dislike for the article: {}'.format(article.title),
                'article': ArticleSerializer(article).data
            }, status=status.HTTP_202_ACCEPTED)
        return Response({
            'message': 'you disliked the article: {}'.format(article.title),
            'article': ArticleSerializer(article).data
        },
        status=status.HTTP_201_CREATED)