from django.db import models
from django.db.models import Avg
from cloudinary.models import CloudinaryField
from ..authentication.models import User
from django.utils.text import slugify
from .utils import generate_slug, get_readtime


class Article(models.Model):
    title = models.CharField(max_length=100, blank=False)
    body = models.TextField(blank=False, null=False)
    description = models.CharField(max_length=128, null=True)
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
        self.read_time = get_readtime(self.body)
        super(Article, self).save(*args, **kwargs)

    class Meta:
        ordering = ('-date_created',)


class ArticleImage(models.Model):
    article = models.ForeignKey(
        Article,
        related_name='article_images',
        on_delete=models.CASCADE)
    image = models.TextField(
        default="https://res.cloudinary.com/dv85uhrw5/image/upload/v1554278002/sample.jpg"
    )
    date_created = models.DateTimeField(
        auto_now=True)

    class Meta:
        ordering = ('-date_created',)


class ReviewsModel(models.Model):
    article = models.ForeignKey(Article, related_name='article_review',
                                on_delete=models.CASCADE)
    review_body = models.TextField()
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
