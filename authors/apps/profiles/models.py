from django.db import models
from authors import settings


class Profile(models.Model):
    """This class represents the model for user profiles"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
