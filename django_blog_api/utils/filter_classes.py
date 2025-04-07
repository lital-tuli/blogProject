from django_filters import rest_framework as filters
from articles.models import Article

class ArticleFilter(filters.FilterSet):
    """
    Filter class for Article model.
    Provides filtering by title, content, author, and tags.
    """
    title = filters.CharFilter(lookup_expr='icontains')
    content = filters.CharFilter(lookup_expr='icontains')
    author = filters.CharFilter(field_name='author__username', lookup_expr='icontains')
    tags = filters.CharFilter(field_name='tags__name', lookup_expr='icontains')

    class Meta:
        model = Article
        fields = ['title', 'content', 'author', 'tags']