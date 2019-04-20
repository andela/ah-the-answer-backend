from collections import OrderedDict
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import APIException
from rest_framework.pagination import LimitOffsetPagination
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
import cloudinary

from .serializers import ArticleSerializer, ArticleImageSerializer, ReviewsSerializer
from rest_framework import status
from .models import Article, ArticleImage, LikeArticles, FavoriteModel, ReviewsModel
from .serializers import (ArticleSerializer, ArticleImageSerializer,
                          FavoriteSerializer)
from .permissions import ReadOnly
from authors.apps.authentication.models import User
from .utils import is_article_owner, has_reviewed, round_average
from .filters import ArticleFilter
from .utils import generate_share_url


def find_article(slug):
    """Method to check if an article exists"""
    try:
        return Article.objects.get(slug=slug)
    except Article.DoesNotExist:
        APIException.status_code = 404
        raise APIException({
            "message": "The article requested does not exist"
        })


def find_favorite(slug):
    """Method checks if an article is available in the FavouriteModel"""
    try:
        return FavoriteModel.objects.get(article__slug=slug)
    except FavoriteModel.DoesNotExist:
        APIException.status_code = 404
        raise APIException({
            "message": "The article requested does not exist in your favorites"
        })


class ArticleView(APIView):
    """Class that contains the method that retrieves all articles and
    creates an article"""
    permission_classes = (IsAuthenticated | ReadOnly,)
    filter_fields = ('author', 'title',)
    pagination_class = LimitOffsetPagination

    def get(self, request):
        """Method to get all articles"""

        # Functionality to search articles by description, author and title
        if request.GET.get('search'):
            search_parameter = request.GET.get('search')

            searched_articles = Article.objects.filter(Q(
                title__icontains=search_parameter) | Q(
                description__icontains=search_parameter) | Q(
                author__username__icontains=search_parameter))
            search_serializer = ArticleSerializer(
                searched_articles, many=True)
            return Response({"articles": search_serializer.data})

        # Functionality to filter articles by author and title
        articles = Article.objects.all()
        article_filter = ArticleFilter()
        filtered_articles = article_filter.filter_queryset(
            request, articles, self)
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(filtered_articles, request)
        if filtered_articles:
            serializer = ArticleSerializer(page, many=True)
            page_results = paginator.get_paginated_response(serializer.data)

            # rename key 'results' to 'articles'
            response = OrderedDict([('articles', v) if k == 'results' else (k, v) for k, v in page_results.data.items()])

            return Response(response, status=200)
        else:
            return Response({"message": "No article found", "articles": []},
                            status=200)

    def post(self, request):
        """Method to create an article"""
        article = request.data.get('article')

        # Create an article from the above data
        serializer = ArticleSerializer(data=article)
        if serializer.is_valid(raise_exception=True):
            article_saved = serializer.save(author=self.request.user)

        return Response({
            "success": "Article '{}' created successfully".format(
                article_saved.title),
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
                    "success": "Article '{}' updated successfully".format(
                        article_saved.title),
                    "article": serializer.data
                })
            response = {"message": "Only the owner can edit this article."}
            return Response(response, status=403)

    def delete(self, request, slug):
        """Method to delete a specific article"""
        article = find_article(slug)

        if self.is_owner(article.author.id, request.user.id) is True:
            article.delete()
            return Response(
                {"message": "Article `{}` has been deleted.".format(slug)},
                status=200)

        response = {"message": "Only the owner can delete this article."}
        return Response(response, status=403)


class ArticleImageView(APIView):
    """Class with methods to upload an image and retrieve all images of an
    article"""
    permission_classes = (IsAuthenticated | ReadOnly,)

    def post(self, request, slug):
        """Method to upload an image"""
        article = find_article(slug)

        if request.FILES:
            try:
                response = cloudinary.uploader.upload(
                    request.FILES['file'],
                    allowed_formats=['png', 'jpg', 'jpeg'])
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
        saved_article = find_article(slug)
        if saved_article.author.pk == self.request.user.pk:
            APIException.status_code = status.HTTP_400_BAD_REQUEST
            raise APIException(
                {"message": "You cannot review your own article"})

        if has_reviewed(saved_article, self.request.user):
            APIException.status_code = status.HTTP_403_FORBIDDEN
            raise APIException(
                {"message": "You have already reviewed this article"})
        review = request.data.get('review')
        serializer = ReviewsSerializer(data=review)
        if serializer.is_valid(raise_exception=True):
            serializer.save(article=saved_article,
                            reviewed_by=self.request.user)

        return Response(
            {
                "success": "Review for '{}' created successfully".format(saved_article.title),
                "Review": serializer.data
            },
            status=201
        )

    def get(self, request, slug):
        try:
            saved_article = find_article(slug)
            average_rating = ReviewsModel.average_rating(saved_article.pk)
            reviews = ReviewsModel.objects.filter(article__slug=slug)
            serializer = ReviewsSerializer(reviews, many=True)
            return Response(
                {
                    "Average Rating": round_average(average_rating.get('rating_value__avg')),

                    "reviews": serializer.data},
            )
        except TypeError:
            APIException.status_code = status.HTTP_404_NOT_FOUND
            raise APIException(
                {"errors": "There are no reviews for that article"})

    def put(self, request, slug, username=None):
        try:
            if username is None:
                raise TypeError
            saved_article = find_article(slug)
            review = ReviewsModel.objects.get(
                article=saved_article, reviewed_by__username=username)
            if review and self.request.user.username == username:
                data = request.data.get('review')
                serializer = ReviewsSerializer(
                    instance=review, data=data, partial=True)
                if serializer.is_valid(raise_exception=True):
                    review_saved = serializer.save()
                    return Response(
                        {"message": "Review for '{}' has been updated.".format(slug),
                         "Review": serializer.data
                         }, status=200)
            return Response(
                {"message": "You are Unauthorized to edit that review"},
                status= 403
                )
        except ObjectDoesNotExist:
            APIException.status_code = status.HTTP_404_NOT_FOUND
            raise APIException(
                {"errors": "That Review does not exist"})
        except TypeError:
            APIException.status_code = status.HTTP_400_BAD_REQUEST
            raise APIException({"errors": "Invalid Url"})
        except Exception as e:
            APIException.status_code = status.HTTP_400_BAD_REQUEST
            raise APIException({"errors": e.detail})

    def delete(self, request, slug, username=None):
        try:
            if username is None:
                raise TypeError
            saved_article = find_article(slug)
            review = ReviewsModel.objects.get(
                article=saved_article, reviewed_by=self.request.user.pk)
            if review and self.request.user.username == username:
                review.delete()
                return Response({"message": "Review for '{}' has been deleted.".format(slug)}, status=200)
            raise APIException(
                {"message": "You are Unauthorized to delete that review"})
        except ObjectDoesNotExist:
            APIException.status_code = status.HTTP_404_NOT_FOUND
            raise APIException(
                {"errors": "That Review does not exist"})
        except TypeError:
            APIException.status_code = status.HTTP_400_BAD_REQUEST
            raise APIException({"errors": "Invalid Url"})
        except Exception as e:
            APIException.status_code = status.HTTP_400_BAD_REQUEST
            raise APIException({"errors": e.detail})

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
                           ' dislike for the article: {}'.format(
                    article.title),
                'article': ArticleSerializer(article).data
            }, status=status.HTTP_202_ACCEPTED)
        return Response({
            'message': 'you disliked the article: {}'.format(article.title),
            'article': ArticleSerializer(article).data
        },
        status=status.HTTP_201_CREATED)


class SocialShareArticleView(APIView):
    permission_classes = (IsAuthenticated | ReadOnly,)

    def get(self, request, slug, provider):
        shared_article = find_article(slug)
        context = {'request': request}

        uri = request.build_absolute_uri()

        # Remove the share/provider/ after the absolute uri
        article_uri = uri.rsplit('share/', 1)[0]
        try:
            share_link = generate_share_url(
                context, provider, shared_article, article_uri)

            if share_link:
                return Response({
                    "share": {
                        "provider": provider,
                        "link": share_link
                    }
                })
        except KeyError:
            return Response({
                "message": "Please select a valid provider - twitter, "
                           "facebook, email, telegram, linkedin, reddit"
            }, status=200)


class FavoriteView(APIView):
    """This views handles the logic for creating and updating
    records of a user's favorite articles
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, slug):
        """
        To favorite an article users only need to hit this endpoint
        /api/article/<slug>/favorite without any body
        :param request:
        :param slug:
        :return: A success message of the article marked as favorite
        """
        article = find_article(slug)
        try:
            fav = FavoriteModel(user=request.user, article=article,
                                favorite=True)
            fav.save()
        except:
            return Response({"message": "Added to favorites"})
        return Response({"article": FavoriteSerializer(fav).data,
                         "message": "Added to favorites"}, status=201)

    def delete(self, request, slug):
        """
        When a user unmarks an article from being favorite, the record is
        deleted from the favorite model
        :param request:
        :param slug:
        :return:
        """
        article = find_article(slug)
        find_favorite(slug)
        FavoriteModel.objects.get(article=article.id,
                                  user=request.user).delete()
        return Response({"message": "Removed from favorites"}, status=200)


class FavoriteListView(APIView):
    """Lists all the articles that a user has marked as favorite"""
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        """
        Gets all articles for that user that they have marked as favorite
        :param request:
        :return:
        """
        favs = FavoriteModel.objects.filter(user=request.user)
        return Response({"articles": FavoriteSerializer(favs, many=True).data,
                         "count": favs.count()}, status=200)
