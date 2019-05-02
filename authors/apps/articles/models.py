from django.db import models
from django.db.models import Avg
from cloudinary.models import CloudinaryField
from ..authentication.models import User
from django.utils.text import slugify
from .utils import generate_slug, get_readtime
from taggit.managers import TaggableManager


class Article(models.Model):
    title = models.CharField(max_length=100, blank=False)
    body = models.TextField(blank=False, null=False)
    description = models.CharField(max_length=128, null=True)
    tags = TaggableManager(blank=True)
    is_published = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=120, db_index=True, unique=True)
    read_time = models.CharField(max_length=10, null=False, blank=False)
    author = models.ForeignKey(
        User, related_name='articles',
        on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_slug(self.title)
        article = Article.objects.filter(slug=self.slug).first()
        if article and article.title != self.title:
            self.slug = generate_slug(self.title)
        self.read_time = get_readtime(self.body)
        super(Article, self).save(*args, **kwargs)

    class Meta:
        ordering = ('-date_created',)


class ArticleImage(models.Model):
    article = models.ForeignKey(
        Article,
        related_name='article_images',
        on_delete=models.CASCADE)
    image_url = models.TextField(
        blank=False, null=True)
    public_id = models.CharField(
        max_length=30, blank=False, null=True)
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    date_created = models.DateTimeField(
        auto_now=True)

    class Meta:
        ordering = ('-date_created',)


class ReviewsModel(models.Model):
    article = models.ForeignKey(Article, related_name='article_review',
                                on_delete=models.CASCADE)
    review_body = models.TextField(blank=True)
    rating_value = models.IntegerField(default=0)
    reviewed_by = models.ForeignKey(
        User, related_name='rating', on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    @staticmethod
    def average_rating(article):
        avg = ReviewsModel.objects.filter(
            article=article).aggregate(Avg('rating_value'))
        return avg
class LikeArticles(models.Model):
    """
    Class handles model for recording like/dislike, user, and article
    """
    user = models.ForeignKey(
        User,
        related_name='liked_by',
        on_delete=models.CASCADE
    )
    article = models.ForeignKey(
        Article,
        related_name='liked',
        db_column='article',
        on_delete=models.CASCADE
    )
    likes = models.IntegerField(null=True)
    created_on = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ('created_on',)

    @staticmethod
    def react_to_article(user, article, value):
        """
        method handles the logic for liking or disliking 
        an article
        """
        user_reaction = LikeArticles.objects.filter(
            user=user,
            article=article
            ).values('likes',)
        # if the 'likes' field in the model is empty, a new instance
        # is created with the user's reaction to an article
        if len(user_reaction) == 0:
            LikeArticles.objects.create(
                user=user,
                article=article,
                likes=value
            )
            return True
        # if the 'likes' field has a character matching the value, the 
        # model takes it that the user wants to revert their reaction
        # to that particular article   
        elif user_reaction[0]['likes'] == value:
            LikeArticles.objects.filter(
                user=user,
                article=article).delete()
            return False
        # if 'likes' field is not empty and the character doesn't match
        # the value provided, that row is deleted and a new instance is 
        # created with the new reaction to the article
        LikeArticles.objects.filter(
            user=user,
            article=article).delete()
        LikeArticles.objects.create(
            user=user,
            article=article,
            likes=value
        )
        return True


class FavoriteModel(models.Model):
    """Model keeps records of all articles that a user has marked as
     favorite"""
    user = models.ForeignKey(User, related_name='favorite',
                             on_delete=models.CASCADE)
    article = models.ForeignKey(Article, related_name='favorite',
                                on_delete=models.CASCADE)
    favorite = models.BooleanField(default=False)
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-date_created',)
        unique_together = ('user', 'article',)

    def __str__(self):
        return '{}-{}'.format(self.user.username, self.article.title)


class Highlight(models.Model):
    """Class that has the fields for highlights made by a user"""
    article = models.ForeignKey(Article, related_name='highlights',
                                on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='highlighter',
                             on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    start = models.PositiveIntegerField()
    end = models.PositiveIntegerField()
    section = models.TextField()
    comment = models.TextField(blank=True, null=False, default='')

    class Meta:
        unique_together = ['user', 'article', 'start', 'end', 'comment']
        ordering = ('-date_created',)
