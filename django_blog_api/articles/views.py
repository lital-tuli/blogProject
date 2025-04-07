from rest_framework import viewsets, filters, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Prefetch, Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie

from .models import Article
from .serializers import ArticleSerializer
from comments.models import Comment
from comments.serializers import CommentSerializer
from core.permissions import IsAdminUserOrReadOnly
from core.utils import error_response
import logging

logger = logging.getLogger(__name__)
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle, ScopedRateThrottle

class ArticleRateThrottle(ScopedRateThrottle):
    scope = 'articles'

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
    throttle_classes = [ArticleRateThrottle]
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tags__name', 'author__username', 'status']
    search_fields = ['title', 'content', 'tags__name', 'author__username']
    ordering_fields = ['publication_date', 'title', 'updated_at', 'comment_count']
    ordering = ['-publication_date']
    
    def get_queryset(self):
        """
        Optimized queryset with select_related and prefetch_related.
        Includes additional filtering options.
        """
        queryset = Article.objects.select_related('author').prefetch_related(
            'tags',
            Prefetch(
                'comments', 
                queryset=Comment.objects.select_related('author').filter(reply_to__isnull=True)
            )
        )
        
        # Add comment count annotation
        queryset = queryset.annotate(comment_count=Count('comments', distinct=True))
        
        # Handle tag filtering
        tag = self.request.query_params.get('tag', None)
        if tag:
            queryset = queryset.filter(tags__name__icontains=tag).distinct()
            
        # Handle author filtering
        author = self.request.query_params.get('author', None)
        if author:
            queryset = queryset.filter(author__username__icontains=author)

        # Handle date range filtering
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        if start_date:
            queryset = queryset.filter(publication_date__gte=start_date)

        if end_date:
            queryset = queryset.filter(publication_date__lte=end_date)

        # Handle status filtering based on user permissions
        status_param = self.request.query_params.get('status', None)

        # Default to showing only published articles for non-authenticated users
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(status='published')
        # For authenticated users, respect the status filter if provided
        elif status_param:
            # Check if user has permissions to see non-published articles
            if (self.request.user.is_staff or 
                self.request.user.groups.filter(name__in=['editors', 'management']).exists()):
                queryset = queryset.filter(status=status_param)
            else:
                # Regular users can only see published articles, even if they request others
                queryset = queryset.filter(status='published')
        else:
            # If no status filter provided and user is authenticated
            if not (self.request.user.is_staff or 
                self.request.user.groups.filter(name__in=['editors', 'management']).exists()):
                # Regular users can only see published articles
                queryset = queryset.filter(status='published')

        # Handle search filtering
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(content__icontains=search_query) | 
                Q(tags__name__icontains=search_query) | 
                Q(author__username__icontains=search_query)
            ).distinct()

        return queryset
    
    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    @method_decorator(vary_on_cookie)
    def list(self, request, *args, **kwargs):
        """
        List articles with caching for better performance.
        Cache varies based on user to handle permission-based content.
        """
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in article list: {str(e)}")
            return error_response("Failed to fetch articles", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @method_decorator(cache_page(60 * 30))  # Cache for 30 minutes
    @method_decorator(vary_on_cookie)
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single article with caching for better performance.
        """
        try:
            return super().retrieve(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error retrieving article: {str(e)}")
            return error_response("Failed to fetch article", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def perform_create(self, serializer):
        """Sets the author to the current user when creating an article."""
        serializer.save(author=self.request.user)
    
    def create(self, request, *args, **kwargs):
        """
        Create a new article.
        Admin/editor only.
        """
        try:
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
        except Exception as e:
            logger.error(f"Error creating article: {str(e)}")
            return error_response("Failed to create article", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def update(self, request, *args, **kwargs):
        """
        Update an article.
        Admin/editor only.
        """
        try:
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
        except Exception as e:
            logger.error(f"Error updating article: {str(e)}")
            return error_response("Failed to update article", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete an article.
        Admin only.
        """
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            return Response(
                {"detail": "Article successfully deleted."}, 
                status=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            logger.error(f"Error deleting article: {str(e)}")
            return error_response("Failed to delete article", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """
        Returns all comments for a specific article.
        
        URL: /api/articles/{pk}/comments/
        Method: GET
        """
        try:
            article = self.get_object()
            # Only get top-level comments (not replies)
            comments = article.comments.filter(reply_to__isnull=True).select_related('author')
            
            page = self.paginate_queryset(comments)
            if page is not None:
                serializer = CommentSerializer(page, many=True, context={'request': request})
                return self.get_paginated_response(serializer.data)
                
            serializer = CommentSerializer(comments, many=True, context={'request': request})
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching article comments: {str(e)}")
            return error_response("Failed to fetch comments", status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    @method_decorator(cache_page(60 * 10))  # Cache for 10 minutes
    def popular(self, request):
        """
        Returns articles ordered by comment count (most commented first).
        
        URL: /api/articles/popular/
        Method: GET
        """
        try:
            articles = self.get_queryset().order_by('-comment_count')
            
            page = self.paginate_queryset(articles)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
                
            serializer = self.get_serializer(articles, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching popular articles: {str(e)}")
            return error_response("Failed to fetch popular articles", status.HTTP_500_INTERNAL_SERVER_ERROR)