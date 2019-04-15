from django.db import models
from authors import settings


class Bookmark(models.Model):
    article_title = modles.Charfield(max_length=100)
    article_id = models.IntegerField()
    user = models.ManyToManyField(
           settings.AUTH_USER_MODEL,
           on_delete=models.CASCADE
    )

    def __str__(self):
        """Defines a human readable name for a
        bookmark database query object."""

        return "{}".format(self.article_title)

