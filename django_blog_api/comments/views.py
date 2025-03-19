
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from articles.models import Article
from .models import Comment
from .serializers import CommentSerializer
from core.permissions import IsAdminOrAuthorOrReadOnly

class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling comment operations.
    
    Provides CRUD operations for comments with appropriate permissions:
    - List/Retrieve: Available to all users
    - Create: Available to authenticated users
    - Update: Limited to the comment author
    - Delete: Limited to admin users
    
    Comments can be filtered by article using the article_pk URL parameter.
    """
    queryset = Comment.objects.select_related('author', 'article', 'reply_to')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrAuthorOrReadOnly]
    
    def perform_create(self, serializer):
        """
        Sets the author to the current user and the article based on URL parameter.
        """
        article_id = self.kwargs.get('article_pk')
        article = get_object_or_404(Article, id=article_id)
        serializer.save(author=self.request.user, article=article)
    
    def get_queryset(self):
        """
        Filters comments by article if article_pk is provided in the URL.
        """
        article_id = self.kwargs.get('article_pk')
        if article_id:
            return Comment.objects.filter(article__id=article_id).select_related('author', 'article', 'reply_to')
        return Comment.objects.all().select_related('author', 'article', 'reply_to')