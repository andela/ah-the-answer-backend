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
        try:
            article = Article.objects.get(title=article_title)
            article_id = article.pk
        except:
            return Response({"error": "No article with that title found."},
                            status=status.HTTP_404_FILE_NOT_FOUND)
        if Bookmark.objects.filter(article_title=article_title).filter(
                                   article_id=article_id).exists():
            return Response({"error": "You already have a bookmark for this "
                            "article."})
        else:
            bookmark = Bookmark(article_title=article_title,
                                article_id=article_id, user=user)
            bookmark.save()
            return Response({"success": "Bookmark for article '{}'created".format(article_title)})
        

        

        






