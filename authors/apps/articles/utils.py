from django.utils.text import slugify
from django_social_share.templatetags import social_share
import secrets
import readtime


def generate_slug(article_title):
    unique_tag = str(secrets.token_hex(6))
    unique_slug = article_title + ' ' + unique_tag
    return slugify(unique_slug)


def get_readtime(article_body):
    """Method to calculate the read time of an article."""
    result = readtime.of_text(article_body)
    return result.text


def generate_share_url(context, provider, article, article_uri):
    social_link = None
    title = '{} by {}\n'.format(article.title, article.author.username)
    if provider == 'twitter':
        social_link = social_share.post_to_twitter(
            context,
            text=title,
            obj_or_url=article_uri
        )['tweet_url']
    elif provider == 'facebook':
        social_link = social_share.post_to_facebook(
            context,
            obj_or_url=article_uri
        )['facebook_url']
    elif provider == 'email':
        text = title
        social_link = social_share.send_email_url(
            context,
            text,
            article_uri
        )['mailto_url']
    elif provider == 'linkedin':
        social_link = social_share.post_to_linkedin(
            context,
            title,
            article_uri
        )['linkedin_url']
    elif provider == 'reddit':
        social_link = social_share.post_to_reddit(
            context,
            title=title,
            obj_or_url=article_uri
        )['reddit_url']
    elif provider == 'telegram':
        social_link = social_share.post_to_telegram(
            context,
            title=title,
            obj_or_url=article_uri
        )['telegram_url']

    return social_link
