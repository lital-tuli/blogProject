from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from articles.models import Article
from .models import Comment
from .serializers import CommentSerializer
from core.permissions import IsAdminOrAuthorOrReadOnly, IsOwnerOrReadOnly
from core.utils import error_response

class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling comment operations.
    
    Endpoints:
    - GET /api/articles/{article_pk}/comments/ - List comments for an article
    - POST /api/articles/{article_pk}/comments/ - Create a comment on an article
    - GET /api/comments/{id}/ - Retrieve a specific comment
    - PUT/PATCH /api/comments/{id}/ - Update a comment (author only)
    - DELETE /api/comments/{id}/ - Delete a comment (admin or author only)
    - POST /api/comments/{id}/reply/ - Reply to a comment
    """
    # Add this line to fix the router registration error
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    def get_permissions(self):
        """
        Custom permissions based on action:
        - Anyone can view comments (list, retrieve)
        - Authenticated users can create comments and replies
        - Only admins can delete a comment
        - Only the author can update their own comments
        """
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        elif self.action in ['create', 'reply']:
            return [permissions.IsAuthenticated()]  # This should allow any authenticated user to create comments
        elif self.action == 'destroy':
            return [permissions.IsAdminUser()]  # Only admins can delete
        elif self.action in ['update', 'partial_update']:
            return [IsOwnerOrReadOnly()]

    def get_queryset(self):
        """
        Filters comments by article if article_pk is provided in the URL.
        For list view, only return top-level comments (not replies).
        """
        queryset = Comment.objects.select_related('author', 'article')
        
        article_id = self.kwargs.get('article_pk')
        if article_id:
            queryset = queryset.filter(article__id=article_id)
            
        # If this is a list action, only return top-level comments
        if self.action == 'list':
            queryset = queryset.filter(reply_to__isnull=True)
            
        return queryset
    
    def create(self, request, *args, **kwargs):
        """
        Create a new comment for an article.
        
        URL: /api/articles/{article_pk}/comments/
        Method: POST
        Auth required: Yes
        """
        article_id = self.kwargs.get('article_pk')
        if not article_id:
            return error_response(
                "Article ID is required to create a comment.",
                status.HTTP_400_BAD_REQUEST
            )
            
        article = get_object_or_404(Article, id=article_id)
        
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                "Invalid comment data", 
                status.HTTP_400_BAD_REQUEST,
                serializer.errors
            )
        
        # Check if this is a reply to another comment
        reply_to_id = request.data.get('reply_to')
        if reply_to_id:
            reply_to = get_object_or_404(Comment, id=reply_to_id)
            # Ensure reply is to a comment on the same article
            if reply_to.article.id != article.id:
                return error_response(
                    "Reply must be to a comment on the same article.",
                    status.HTTP_400_BAD_REQUEST
                )
            serializer.save(author=request.user, article=article, reply_to=reply_to)
        else:
            serializer.save(author=request.user, article=article)
            
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def list(self, request, *args, **kwargs):
        """
        List comments for an article, hierarchically organized.
        
        URL: /api/articles/{article_pk}/comments/
        Method: GET
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def perform_create(self, serializer):
        """
        Sets the author to the current user when creating a comment.
        This is only used when not overriding create() method.
        """
        serializer.save(author=self.request.user)
    
    def update(self, request, *args, **kwargs):
        """
        Update a comment (author only).
        
        URL: /api/comments/{id}/
        Method: PUT/PATCH
        Auth required: Yes (must be author)
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=kwargs.get('partial', False))
        
        if not serializer.is_valid():
            return error_response(
                "Invalid comment data", 
                status.HTTP_400_BAD_REQUEST,
                serializer.errors
            )
            
        self.perform_update(serializer)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """
        Create a reply to an existing comment.
        
        URL: /api/comments/{pk}/reply/
        Method: POST
        Auth required: Yes
        """
        parent_comment = self.get_object()
        
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                "Invalid reply data", 
                status.HTTP_400_BAD_REQUEST,
                serializer.errors
            )
            
        serializer.save(
            author=request.user,
            article=parent_comment.article,
            reply_to=parent_comment
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)