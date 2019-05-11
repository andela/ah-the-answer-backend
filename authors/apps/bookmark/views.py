from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import APIException

from ..articles.models import Article
from ..bookmark.models import Bookmark
from ..authentication.models import User


class CreateBookmark(APIView):
    """
    Contains views that allow a user to
    create a single bookmark and fetch an article.
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, article_id):
        """
        Accepts an article id argument as an int from the URL. Creates a
        bookmark object for an existing article. It then creates a
        relationship between the current user object and the article bookmark.
        """
        user = self.request.user
        username = user.username
        try:
            article = Article.objects.get(id=article_id)
        except:
            return Response({"error": "No article with that id found."},
                            status=status.HTTP_404_NOT_FOUND)
        bookmark = Bookmark.objects.filter(article_id=article_id)
        if bookmark.exists() and not bookmark[0].user.filter(username=username).exists():
            bookmark[0].user.add(user)
            return Response({"success": "Bookmark for article '{}'created.".format(article.title)}, status=status.HTTP_201_CREATED)
        elif bookmark.exists() and bookmark[0].user.filter(username=username).exists():
            return Response({"error": "Article bookmark for this "
                            "user already exists."},
                            status=status.HTTP_400_BAD_REQUEST)
        else:
            new_bookmark = Bookmark(article_title=article.title,
                                    article_id=article_id)
            new_bookmark.save()
            new_bookmark.user.add(user)
            return Response({"success": "Bookmark for article '{}'created.".format(article.title)}, 
                            status=status.HTTP_201_CREATED)

    def get(self, request, article_id):
        """
        Fetches the related article object from a bookmark.
        """
        try:
            fetch_id = Bookmark.objects.get(article_id=article_id).article_id
        except:
            return Response({"error": "No bookmark for that article found."}, status=status.HTTP_404_NOT_FOUND)
        article = Article.objects.filter(id=fetch_id).values()
        return Response({"success": article}, status=status.HTTP_200_OK)


class RetrieveBookmarks(APIView):
    """
    Returns a list of article titles
    that the user has bookmarked.
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        bookmark_list = user.bookmark_set.all()
        bookmarks = [i.article_title for i in bookmark_list]
        return Response({"success": bookmarks}, status=status.HTTP_200_OK)
