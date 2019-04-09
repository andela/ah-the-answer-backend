from django.db import models
from cloudinary.models import CloudinaryField
from ..authentication.models import User
from django.utils.text import slugify
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework import status
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

class LikeArticles(models.Model):
    user = models.ForeignKey(
        User,
        related_name='liked_by',
        on_delete=models.CASCADE
    )
    article = models.ForeignKey(
        Article,
        to_field='slug',
        related_name='liked',
        db_column='article',
        on_delete=models.CASCADE
    )
    likes = models.IntegerField(null=True)
    dislikes = models.IntegerField(null=True)
    created_on = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ('created_on',)

    @staticmethod
    def retrieve_article(slug):
        """Method gets a single article"""
        article = get_object_or_404(Article, slug=slug)
        return article

    @staticmethod
    def like_by_user(user, slug, ArticleSerializer, value):
        """This method holds logic for like, dislike, or revoking"""
        try:
            likes = LikeArticles.objects.filter(user=user, article=slug)
            article = LikeArticles.retrieve_article(slug=slug)
        except:
            APIException.status_code = status.HTTP_404_NOT_FOUND
            raise APIException(
                {
                    'article': {
                        'message': 'Article requested does not exist'
                    }
                }
            )
        if not likes:
            if value == 1:
                LikeArticles.objects.create(
                    user=user,
                    article=article,
                    likes=value
                )
                return Response({
                    'message': 'you liked {} article'.format(slug),
                    'article': ArticleSerializer(article).data
                },
                status=status.HTTP_201_CREATED
                )
            LikeArticles.objects.create(
                user=user,
                article=article,
                likes=value
            )
            return Response({
                'message': 'you have disliked {} article'.format(slug),
                'article': ArticleSerializer(article).data
            },
            status=status.HTTP_201_CREATED
            )
        likes.delete()
        return Response({
            'message': 'you have reverted your like/dislike for {} article'.format(slug),
            'article': ArticleSerializer(article).data
        }, status=status.HTTP_202_ACCEPTED)