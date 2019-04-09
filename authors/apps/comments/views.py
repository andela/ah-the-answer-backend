from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import views, permissions, status, response, exceptions
from .serializers import CommentSerializer
from authors.apps.comments.models import Comment
from authors.apps.articles.models import Article
from authors.apps.articles.permissions import ReadOnly


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

    def post(self, request, slug):

        serializer = CommentSerializer(data=request.data.get('comment'))
        article = Article.objects.get(slug=slug)

        if serializer.is_valid(raise_exception=True):
            save_comment = serializer.save(
                author=self.request.user,
                article=article
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

    def put(self, request, slug, pk):
        comment = Comment.objects.get(id=pk)
        serializer = CommentSerializer(comment)

        update_body = request.data['comment']['body']

        if len(update_body) < 1:
            raise exceptions.ValidationError("Body should not be empty")

        try:
            self.validate_user(comment.author, self.request.user)
            comment.body = update_body
            comment.save()

            return response.Response(
                {
                    "success": "Comment updated successful",
                    "comment": serializer.data
                }
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
