from rest_framework import viewsets, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Article
from .serializers import ArticleSerializer
from core.permissions import IsAdminUserOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from comments.serializers import CommentSerializer

class ArticleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling article operations.
    
    Provides CRUD operations for articles with appropriate permissions:
    - List/Retrieve: Available to all users
    - Create/Update/Delete: Limited to admin users or editors
    
    Includes filtering by tag and author, as well as search functionality.
    """
    queryset = Article.objects.select_related('author').prefetch_related('tags')
    serializer_class = ArticleSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tags__name', 'author__username']
    search_fields = ['title', 'content', 'tags__name', 'author__username']
    ordering_fields = ['publication_date', 'title']
    ordering = ['-publication_date']
    
    def get_queryset(self):
        """
        Customizes the queryset based on query parameters.
        
        Handles specific filtering:
        - Filter by tag with 'tag' parameter
        - Filter by author with 'author' parameter
        """
        queryset = Article.objects.select_related('author').prefetch_related('tags')
        
        # Handle specific tag filtering
        tag = self.request.query_params.get('tag', None)
        if tag:
            queryset = queryset.filter(tags__name__icontains=tag)
            
        # Handle author filtering
        author = self.request.query_params.get('author', None)
        if author:
            queryset = queryset.filter(author__username__icontains=author)
            
        return queryset
    
    def perform_create(self, serializer):
        """Sets the author to the current user when creating an article."""
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """
        Returns all comments for a specific article.
        
        URL: /api/articles/{pk}/comments/
        Method: GET
        """
        article = self.get_object()
        comments = article.comments.filter(reply_to__isnull=True)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """
        Returns articles ordered by comment count (most commented first).
        
        URL: /api/articles/popular/
        Method: GET
        """
        articles = Article.objects.annotate(
            comment_count=Count('comments')
        ).order_by('-comment_count')
        
        page = self.paginate_queryset(articles)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(articles, many=True)
        return Response(serializer.data)