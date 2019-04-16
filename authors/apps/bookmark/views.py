from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import APIException

from ..articles.models import Article
from ..bookmark.models import Bookmark
from ..authentication.models import User


class CreateRetrieveBookmark(APIView):
    """This class allows contains views that allow a user to
    create a bookmark as well as retrieve all of their bookmarked articles."""
    permission_classes = (IsAuthenticated,)

    def post(self, request, article_title):
        user = self.request.user
        username = user.username
        try:
            article = Article.objects.get(title=article_title)
            article_id = article.pk
        except:
            return Response({"error": "No article with that title found."},
                            status=status.HTTP_404_NOT_FOUND)
        bookmark = Bookmark.objects.filter(article_title=article_title).filter(
                                           article_id=article_id)
        if bookmark.exists() and not bookmark[0].user.filter(username=username).exists():
            bookmark[0].user.add(user)
            return Response({"success": "Bookmark for article '{}'created.".format(article_title)}, status=status.HTTP_201_CREATED)
        elif bookmark.exists() and bookmark[0].user.filter(username=username).exists():
            return Response({"error": "Article bookmark for this "
                            "user already exists."},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            new_bookmark = Bookmark(article_title=article_title,
                                    article_id=article_id)
            new_bookmark.save()
            new_bookmark.user.add(user)
            return Response({"success": "Bookmark for article '{}'created.".format(article_title)})


class RetrieveBookmarks(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        bookmark_list = user.bookmark_set.all()
        bookmarks = [i.article_title for i in bookmark_list]
        return Response({"success": bookmarks})

    

        

        






