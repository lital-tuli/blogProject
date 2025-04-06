# django_blog_api/articles/views.py
from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Prefetch
from .models import Article
from .serializers import ArticleSerializer
from comments.models import Comment
from comments.serializers import CommentSerializer
from core.permissions import IsAdminUserOrReadOnly
from core.utils import error_response

class ArticleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling article operations.
    
    Endpoints:
    - GET /api/articles/ - List all articles
    - GET /api/articles/?search={term} - Search articles
    - GET /api/articles/?tag={tag} - Filter articles by tag
    - GET /api/articles/?author={username} - Filter articles by author
    - GET /api/articles/{id}/ - Get specific article
    - POST /api/articles/ - Create a new article (admin/editor only)
    - PUT/PATCH /api/articles/{id}/ - Update an article (admin/editor only)
    - DELETE /api/articles/{id}/ - Delete an article (admin only)
    - GET /api/articles/popular/ - List articles by popularity (comment count)
    - GET /api/articles/{id}/comments/ - Get comments for a specific article
    """
    # Add this line to fix the router registration error
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tags__name', 'author__username']
    search_fields = ['title', 'content', 'tags__name', 'author__username']
    ordering_fields = ['publication_date', 'title', 'updated_at']
    ordering = ['-publication_date']
    
    def get_queryset(self):
        """
        Optimized queryset with select_related and prefetch_related.
        """
        queryset = Article.objects.select_related('author').prefetch_related(
            'tags',
            Prefetch('comments', queryset=Comment.objects.select_related('author'))
        )
        
        # Add comment count annotation
        queryset = queryset.annotate(comment_count=Count('comments', distinct=True))
        
        # Handle filtering
        tag = self.request.query_params.get('tag', None)
        if tag:
            queryset = queryset.filter(tags__name__icontains=tag).distinct()
            
        author = self.request.query_params.get('author', None)
        if author:
            queryset = queryset.filter(author__username__icontains=author)
            
        status_param = self.request.query_params.get('status', None)
        if status_param and self.request.user.is_authenticated and (
            self.request.user.is_staff or 
            self.request.user.groups.filter(name__in=['editors', 'management']).exists()
        ):
            queryset = queryset.filter(status=status_param)
        else:
            # Non-admins/editors can only see published articles
            queryset = queryset.filter(status='published')
                
        return queryset
    
    def perform_create(self, serializer):
        """Sets the author to the current user when creating an article."""
        serializer.save(author=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """
        Create a new article.
        Admin/editor only.
        """
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                "Invalid article data", 
                status.HTTP_400_BAD_REQUEST,
                serializer.errors
            )
            
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        """
        Update an article.
        Admin/editor only.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        
        if not serializer.is_valid():
            return error_response(
                "Invalid article data", 
                status.HTTP_400_BAD_REQUEST,
                serializer.errors
            )
            
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete an article.
        Admin only.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Article successfully deleted."}, 
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """
        Returns all comments for a specific article.
        
        URL: /api/articles/{pk}/comments/
        Method: GET
        """
        article = self.get_object()
        # Only get top-level comments (not replies)
        comments = article.comments.filter(reply_to__isnull=True).select_related('author')
        
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = CommentSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
            
        serializer = CommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """
        Returns articles ordered by comment count (most commented first).
        
        URL: /api/articles/popular/
        Method: GET
        """
        articles = self.get_queryset().order_by('-comment_count')
        
        page = self.paginate_queryset(articles)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(articles, many=True)
        return Response(serializer.data)