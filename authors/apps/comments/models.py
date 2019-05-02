from django.db import models
from authors.apps.authentication.models import User
from authors.apps.articles.models import Article
from simple_history.models import HistoricalRecords


class Comment(models.Model):
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    body = models.TextField()
    comment_history = HistoricalRecords()
    author = models.ForeignKey(
        User,
        related_name="comments",
        on_delete=models.CASCADE
    )
    article = models.ForeignKey(
        Article,
        related_name="comments",
        on_delete=models.CASCADE
    )

    def __str__(self):
        return self.body[:15] + "..."

    class Meta:
        ordering = ["-createdAt"]
