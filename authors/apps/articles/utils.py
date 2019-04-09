from django.utils.text import slugify
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
