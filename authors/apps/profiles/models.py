from django.db import models
from authors import settings
from cloudinary import CloudinaryImage
from cloudinary.models import CloudinaryField


class Profile(models.Model):
    """This class represents the model for Author's Haven user profile
    information."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    user_bio = models.TextField(help_text='Write a brief '
                                'description about yourself.')
    name = models.CharField(max_length=50, help_text='Enter your first '
                            'and last names.')
    number_of_followers = models.IntegerField(default=0)
    number_of_followings = models.IntegerField(default=0)
    total_articles = models.IntegerField(default=0)
    avatar = CloudinaryField(
        "image", default='smiling_penguin.png')

    def get_cloudinary_url(self):
        """
        Retrieves saved avatar model path and generates a cloudinary url that
        links to the location of the file online
        """

        avatar_url = CloudinaryImage(str(self.avatar)).build_url(
            width=200, height=200, gravity="face",
            background="black", radius="max", crop="thumb")
        return avatar_url

    @property
    def get_username(self):
        """
        Gets username from through the OneToOne relationship
        through 'user' for profile display
        """
        return self.user.username

    def __str__(self):
        """
       Human readable format of a direct db call
        """

        return "{}".format(self.user.username)
