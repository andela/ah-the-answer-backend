from django.utils.text import slugify
import secrets


def generate_slug(article_title):
    unique_tag = str(secrets.token_hex(6))
    unique_slug = article_title + ' ' + unique_tag
    return slugify(unique_slug)
