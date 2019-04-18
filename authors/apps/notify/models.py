from django.db import models
from authors.apps.authentication.models import User


class Notification(models.Model):
    body = models.TextField()
    createdAt = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    recepient = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.body[:10]

    class Meta:
        ordering = ['-createdAt']
