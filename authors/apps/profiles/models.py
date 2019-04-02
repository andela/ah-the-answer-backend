from django.db import models
from cloudinary.models import CloudinaryField
from authors import settings


class Profile(models.Model):
    """This class represents the model for Author's Haven user profiles."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    user_bio = models.CharField(max_length=300, help_text='Write a brief '
                                'description about yourself.')
    name = models.CharField(max_length=50, help_text='Enter your first '
                            'and last names.')
    number_of_followers = models.IntegerField(default=0)
    number_of_followings = models.IntegerField(default=0)
    total_articles = models.IntegerField(default=0)
    avatar = CloudinaryField('image', blank=True, null=True)

    def __str__(self):
        return "{}".format(self.user.username)
