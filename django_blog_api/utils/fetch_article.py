from rest_framework import serializers
from articles.models import Article

class ArticleFromURL:
    """
    Field default callable to fetch an article from the URL parameters.
    To be used with serializer fields.
    """
    requires_context = True

    def __call__(self, serializer_field):
        view = serializer_field.context.get('view', None)
        if view and hasattr(view, 'kwargs'):
            article_id = view.kwargs.get('article_id')
            if article_id:
                try:
                    return Article.objects.get(id=article_id)
                except Article.DoesNotExist:
                    raise serializers.ValidationError("Article not found.")
        raise serializers.ValidationError("Article ID is required in the URL.")