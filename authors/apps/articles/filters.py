from django_filters.rest_framework import DjangoFilterBackend
from .models import Article
from django.core.paginator import Paginator


class ArticleFilter(DjangoFilterBackend):
    def filter_queryset(self, request, queryset, view):
        filter_class = self.get_filter_class(view, queryset)
        author = request.query_params.get('author')
        if author:
            return filter_class(request.query_params, queryset=Article.objects.all().filter(author__username=author), request=request).qs

        # pagination
        page = request.GET.get('page')
        article_list = Article.objects.all()
        paginator = Paginator(article_list, 10)
        if page:
            page_articles = paginator.get_page(page)
            return page_articles

        articles = paginator.get_page(1)
        return articles
        