from django_filters.rest_framework import DjangoFilterBackend


class ArticleFilter(DjangoFilterBackend):
    def filter_queryset(self, request, queryset, view):
        filter_class = self.get_filter_class(view, queryset)
        return filter_class(request.query_params, queryset=queryset, request=request).qs
