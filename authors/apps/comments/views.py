import os
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import views, permissions, status, response, exceptions
from .serializers import CommentSerializer, CommentHistorySerializer
from authors.apps.comments.models import Comment, LikeDislikeComment
from authors.apps.articles.models import Article
from authors.apps.articles.permissions import ReadOnly
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from authors.apps.notify.views import NotificationsView
from drf_yasg.utils import swagger_auto_schema
from ..articles.views import find_article


def find_comment(comment_id):
    """
    Confirms that a comment exists
    :param comment_id: the comment id
    :return:
    """
    try:
        return Comment.objects.get(pk=comment_id)
    except Comment.DoesNotExist:
        APIException.status_code = 404
        raise APIException({
            "message": "The comment does not exist"
        })


class CommentsCreateList(views.APIView):
    permission_classes = (permissions.IsAuthenticated | ReadOnly,)

    def get(self, request, slug):
        article = Article.objects.get(slug=slug)
        comments = Comment.objects.filter(article=article)
        serializer = CommentSerializer(comments, many=True)
        return response.Response(
            {
                "comments": serializer.data
            }
        )

    @swagger_auto_schema(request_body=CommentSerializer,
                         responses={201: CommentSerializer(),
                                    400: "Bad Request",
                                    403: "Forbidden",
                                    404: "Not Found"})
    def post(self, request, slug):
        serializer = CommentSerializer(data=request.data.get('comment'))
        article = Article.objects.get(slug=slug)

        if serializer.is_valid(raise_exception=True):
            save_comment = serializer.save(
                author=self.request.user,
                article=article
            )
            NotificationsView.send_notification(
                "@{0} commented on article {1}".format(
                    self.request.user.username,
                    os.getenv('DOMAIN') +
                    '/api/articles/' +
                    serializer.data.get('article').get('slug') + '/'
                ),
                serializer.data,
                'new-comment'
            )
            return response.Response(
                {
                    "success": "Comment created successfully",
                    "comment": serializer.data
                },
                status=status.HTTP_201_CREATED
            )


class CommentsDetail(views.APIView):
    permission_classes = (permissions.IsAuthenticated | ReadOnly,)
    validation_message = (
        "Only the author of this comment can make the requested changes"
    )

    def get(self, request, slug, pk):
        try:
            comment = Comment.objects.get(id=pk)
            serializer = CommentSerializer(comment)
            return response.Response(
                {
                    "comments": serializer.data
                }
            )
        except ObjectDoesNotExist:
            return response.Response(
                {
                    "errors": "The record does not exist in the database"
                },
                status.HTTP_404_NOT_FOUND
            )

    @swagger_auto_schema(request_body=CommentSerializer,
                         responses={201: CommentSerializer(),
                                    400: "Bad Request",
                                    403: "Forbidden",
                                    404: "Not Found"})
    def put(self, request, slug, pk):
        try:
            comment = Comment.objects.get(id=pk)
            serializer = CommentSerializer(comment)
            update_body = request.data['comment']['body'].strip()

            self.validate_user(comment.author, self.request.user)
            comment.body = update_body
            comment.save()

            return response.Response(
                {
                    "success": "Comment updated successful",
                    "comment": serializer.data
                },
                status.HTTP_200_OK
            )
        except ObjectDoesNotExist:
            return response.Response(
                {
                    "errors": "The record does not exist in the database"
                },
                status.HTTP_404_NOT_FOUND
            )
        except exceptions.ValidationError:
            return response.Response(
                {
                    "errors": self.validation_message
                },
                status.HTTP_401_UNAUTHORIZED
            )

    def delete(self, request, slug, pk):
        try:
            comment = Comment.objects.get(id=pk)
            self.validate_user(comment.author, self.request.user)
            comment.delete()
            return response.Response(
                {
                    "success": "Comment deleted successfully"
                },
                status=status.HTTP_200_OK
            )
        except ObjectDoesNotExist:
            return response.Response(
                {
                    "errors": "The record does not exist in the database"
                },
                status.HTTP_404_NOT_FOUND
            )
        except exceptions.ValidationError:

            return response.Response(
                {
                    "errors": self.validation_message
                },
                status.HTTP_401_UNAUTHORIZED
            )

    def validate_user(self, comment_user, user):
        if comment_user != user:
            raise exceptions.ValidationError()
        else:
            return True


class LikeCommentView(views.APIView):
    """
    Thu endpoint is used for liking a comment, it implements only the POST
    method
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk):
        """
        POST endpoint allows authenticated users to like a comment
        :param request:
        :param slug
        :param pk: the comment id
        :return: response with liked comment
        """
        target_comment = find_comment(pk)
        liked = LikeDislikeComment.react_to_comment(
            request.user, target_comment, 1)
        if not liked:
            return response.Response({
                'message':
                    'Your like has been reverted for comment: {}'.format(
                        target_comment.id),
                'comment': CommentSerializer(target_comment).data,
                'likes': LikeDislikeComment.get_count_like(target_comment),
                'dislikes': LikeDislikeComment.get_count_dislike(
                    target_comment)
            }, status=status.HTTP_202_ACCEPTED)
        return response.Response({
            'message': 'You liked comment: {}'.format(target_comment.id),
            'comment': CommentSerializer(target_comment).data,
            'likes': LikeDislikeComment.get_count_like(target_comment),
            'dislikes': LikeDislikeComment.get_count_dislike(
                target_comment)
        },
            status=status.HTTP_201_CREATED)


class DislikeCommentView(views.APIView):
    """
    Class for POST view allowing authenticated users to dislike articles
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk):
        """
        POST endpoint allows authenticated users to dislike a comment
        :param request:
        :param slug:
        :param pk: primary key of the comment
        :return:
        """
        target_comment = find_comment(pk)
        disliked = LikeDislikeComment.react_to_comment(
            request.user, target_comment, 0)
        if not disliked:
            return response.Response({
                'message':
                    'Your dislike has been reverted for comment: {}'.format(
                        target_comment.id),
                'comment': CommentSerializer(target_comment).data,
                'likes': LikeDislikeComment.get_count_like(target_comment),
                'dislikes': LikeDislikeComment.get_count_dislike(
                    target_comment)
            }, status=status.HTTP_202_ACCEPTED)
        return response.Response({
            'message': 'You disliked comment: {}'.format(target_comment.id),
            'comment': CommentSerializer(target_comment).data,
            'likes': LikeDislikeComment.get_count_like(target_comment),
            'dislikes': LikeDislikeComment.get_count_dislike(
                target_comment)
        },
            status=status.HTTP_201_CREATED)


class CommentRatings(views.APIView):
    """
    Class for GET view allowing any user to view the ratings of a comment
    """
    def get(self, request, pk):
        """
        GET endpoint allows any users to view a comment's likes/dislikes
        :param pk: primary key of the comment
        :return:
        """
        target_comment = find_comment(pk)
        return response.Response({
            'comment': CommentSerializer(target_comment).data,
            'likes': LikeDislikeComment.get_count_like(target_comment),
            'dislikes': LikeDislikeComment.get_count_dislike(
                target_comment)
        },
            status=status.HTTP_200_OK)


class CommentRatingCheck(views.APIView):
    """
    Class for GET view which checks if a user has previosuly rated a comment
    """
    def get(self, request, username, pk):
        """
        GET endpoint checks if a given user has like/disliked a given comment
        :param username: user's username
        :param pk: primary key of the comment
        :return: boolean
        """
        if LikeDislikeComment.objects.filter(user__username=username, comment__pk=pk).exists():
            return Response({
                'response': 'User has already liked/disliked this comment.',
                'hasRated': True
                }, status=status.HTTP_200_OK)
        return Response({
            'response': 'User has not liked/disliked this comment, or this comment does not exist.',
            'hasRated': False
        }, status=status.HTTP_200_OK)


class CommentHistoryView(views.APIView):

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, slug, pk):
        try:
            find_article(slug)
            comment = Comment.objects.get(id=pk)
            if comment and comment.author == self.request.user:
                serializer = CommentHistorySerializer(comment)
                return response.Response(
                    serializer.data,
                )
            exceptions.APIException.status_code = status.HTTP_403_FORBIDDEN
            raise exceptions.APIException({
                "errors": "You are not authorized to view this history"
            })
        except ObjectDoesNotExist:
            return response.Response(
                {
                    "errors": "There is no edit history for that comment"
                },
                status.HTTP_404_NOT_FOUND
            )
