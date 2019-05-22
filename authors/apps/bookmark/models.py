from django.db import models
from authors import settings
from authors.apps.articles.models import Article


class Bookmark(models.Model):
    article_title = models.CharField(max_length=100)
    user = models.ManyToManyField(
           settings.AUTH_USER_MODEL
    )
    bookmarked_article = models.ForeignKey(
        Article,
        related_name="bookmarks",
        on_delete=models.CASCADE,
        default=1,
    )
    article_id = models.IntegerField(default=0)
    article_slug = models.TextField(blank=True, null=False)

    def __str__(self):
        """Defines a human readable name for a
        bookmark database query object."""

        return "{}".format(self.article_title)
