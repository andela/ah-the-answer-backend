from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException
import cloudinary

from .models import Article, ArticleImage, ReviewsModel
from .serializers import ArticleSerializer, ArticleImageSerializer, ReviewsSerializer
from .permissions import ReadOnly
from authors.apps.authentication.models import User
from .utils import is_article_owner, has_reviewed


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

    def get(self, request):
        """Method to get all articles"""
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        return Response({"articles": serializer.data})

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


class ReviewView(APIView):
    permission_classes = (IsAuthenticated | ReadOnly,)

    def post(self, request, slug):

        saved_article = Article.objects.get(slug=slug)
        if is_article_owner(saved_article.author.pk, self.request.user.pk):
            APIException.status_code = status.HTTP_400_BAD_REQUEST
            raise APIException(
                {"message": "You cannot review your own article"})

        if has_reviewed(saved_article, self.request.user):
            raise APIException(
                {"message": "You have already reviewed this article"})
        review = request.data.get('review')
        serializer = ReviewsSerializer(data=review)
        if serializer.is_valid(raise_exception=True):
            serializer.save(article=saved_article,
                            reviewed_by=self.request.user)

        return Response(
            {
                "success": "Review for {} created successfully".format(saved_article.title),
                "Review": serializer.data
            },
            status=201
        )

    def get(self, request, slug):
        try:
            saved_article = Article.objects.get(slug=slug)
            average_rating = ReviewsModel.average_rating(saved_article.pk)
            reviews = ReviewsModel.objects.filter(article__slug=slug)
            serializer = ReviewsSerializer(reviews, many=True)
            return Response(
                {"Average Rating": round(average_rating.get('rating_value__avg') + 0.005),
                 "reviews": serializer.data},
            )
        except TypeError:
            APIException.status_code = status.HTTP_404_NOT_FOUND
            raise APIException(
                {"errors": "There are no reviews for that article"})

    def put(self, request, slug):
        try:
            saved_article = Article.objects.get(slug=slug)
            review = ReviewsModel.objects.get(
                article=saved_article, reviewed_by=self.request.user.pk)
            if review:
                data = request.data.get('review')
                serializer = ReviewsSerializer(
                    instance=review, data=data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    review_saved = serializer.save()
                    return Response(
                        {"message": "Review for '{}' has been updated.".format(slug),
                         "Review": serializer.data
                         }, status=200)
            raise APIException(
                {"message": "You are unathorized to edit that review"})
        except Exception as e:
            raise APIException({"errors": e})

    def delete(self, request, slug):
        try:
            saved_article = Article.objects.get(slug=slug)
            review = ReviewsModel.objects.get(
                article=saved_article, reviewed_by=self.request.user.pk)
            if review:
                review.delete()
                return Response({"message": "Review for '{}' has been deleted.".format(slug)}, status=200)
            raise APIException(
                {"message": "You are unathorized to delete that review"})
        except Exception as e:
            raise APIException({"errors": e})
