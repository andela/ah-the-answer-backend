from django.utils.text import slugify
from django_social_share.templatetags import social_share
import secrets
import readtime
from decimal import Decimal, ROUND_HALF_UP


def generate_slug(article_title):
    unique_tag = str(secrets.token_hex(6))
    unique_slug = article_title + ' ' + unique_tag
    return slugify(unique_slug)


def get_readtime(article_body):
    """Method to calculate the read time of an article."""
    result = readtime.of_html(article_body)
    return result.text


def twitter_share_url(context, article_uri, title):
    return social_share.post_to_twitter(
        context,
        text=title,
        obj_or_url=article_uri
    )['tweet_url']


def facebook_share_url(context, article_uri, title):
    return social_share.post_to_facebook(
        context,
        obj_or_url=article_uri
    )['facebook_url']


def email_share_url(context, article_uri, title):
    text = title
    return social_share.send_email_url(
        context,
        text,
        article_uri
    )['mailto_url']


def linkedin_share_url(context, article_uri, title):
    return social_share.post_to_linkedin(
        context,
        title,
        article_uri
    )['linkedin_url']


def reddit_share_url(context, article_uri, title):
    return social_share.post_to_reddit(
        context,
        title=title,
        obj_or_url=article_uri
    )['reddit_url']


def telegram_share_url(context, article_uri, title):
    return social_share.post_to_telegram(
        context,
        title=title,
        obj_or_url=article_uri
    )['telegram_url']


def generate_share_url(context, provider, article, article_uri):
    title = '{} by {}\n'.format(article.title, article.author.username)

    providers = {
        'twitter': twitter_share_url(
            context, article_uri, title),
        'facebook': facebook_share_url(
            context, article_uri, title),
        'email': email_share_url(
            context, article_uri, title),
        'linkedin': linkedin_share_url(
            context, article_uri, title),
        'reddit': reddit_share_url(
            context, article_uri, title),
        'telegram': telegram_share_url(
            context, article_uri, title)
    }

    return providers[provider]


def is_article_owner(author, reviewer):
    if author == reviewer:
        return True



def has_reviewed(article, reviewer):
    from .models import ReviewsModel

    count = ReviewsModel.objects.filter(article=article,
                                        reviewed_by=reviewer).count()
    if count > 0:
        return True


def round_average(average):
    average = Decimal(average).quantize(0, ROUND_HALF_UP)
    return int(average)
