from django_filters.rest_framework import DjangoFilterBackend
from .models import Article


class ArticleFilter(DjangoFilterBackend):
    def filter_queryset(self, request, queryset, view):
        filter_class = self.get_filter_class(view, queryset)
        author = request.query_params.get('author')
        if author:
            return filter_class(request.query_params, queryset=Article.objects.all().filter(author__username=author), request=request).qs
        return filter_class(request.query_params, queryset=queryset, request=request).qs
