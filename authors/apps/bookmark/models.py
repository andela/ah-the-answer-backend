from django.db import models
from authors import settings


class Bookmark(models.Model):
    article_title = models.CharField(max_length=100)
    article_id = models.IntegerField()
    user = models.ManyToManyField(
           settings.AUTH_USER_MODEL
    )

    def __str__(self):
        """Defines a human readable name for a
        bookmark database query object."""

        return "{}".format(self.article_title)

