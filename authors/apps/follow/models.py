from django.db import models
from authors import settings


class Follows(models.Model):
    """This class represents the model for Author's Haven that records user
    followers and followings."""
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    followed_user = models.CharField(max_length=100)
    following_user = models.CharField(max_length=100)

    def __str__(self):
        return "{} is following {}".format(self.following_user,
                                           self.followed_user)
