from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
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
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    def get_permissions(self):
        """
        Custom permissions based on action:
        - Anyone can view comments (list, retrieve)
        - Authenticated users can create comments
        - Admin users can delete any comment
        - Users can only edit their own comments
        """
        if self.action in ['list', 'retrieve']:
            # Allow anyone to view comments
            return [permissions.AllowAny()]
        elif self.action == 'create':
            # Only authenticated users can create comments
            return [permissions.IsAuthenticated()]
        elif self.action == 'destroy':
            # Only admin users can delete comments
            return [permissions.IsAdminUser()]
        else:
            # For update/partial_update, use IsAuthenticated
            return [permissions.IsAuthenticated(), IsAdminOrAuthorOrReadOnly()]
    
    def perform_create(self, serializer):
        """
        Sets the author to the current user and the article based on URL parameter.
        """
        article_id = self.kwargs.get('article_pk')
        article = get_object_or_404(Article, id=article_id)
        
        # Check if this is a reply to another comment
        reply_to_id = self.request.data.get('reply_to')
        if reply_to_id:
            reply_to = get_object_or_404(Comment, id=reply_to_id)
            serializer.save(author=self.request.user, article=article, reply_to=reply_to)
        else:
            serializer.save(author=self.request.user, article=article)

    def perform_update(self, serializer):
        """
        Only allow users to update their own comments
        """
        instance = self.get_object()
        if instance.author != self.request.user and not self.request.user.is_staff:
            self.permission_denied(
                self.request,
                message="You can only edit your own comments."
            )
        serializer.save()

    def get_queryset(self):
        """
        Filters comments by article if article_pk is provided in the URL.
        Also only shows top-level comments (no replies) when listing.
        """
        queryset = Comment.objects.all()
        
        article_id = self.kwargs.get('article_pk')
        if article_id:
            queryset = queryset.filter(article__id=article_id)
            
        # If this is a list action, only return top-level comments
        if self.action == 'list':
            queryset = queryset.filter(reply_to__isnull=True)
            
        return queryset
    
    @action(detail=True, methods=['post'])
    def reply(self, request, pk=None):
        """
        Create a reply to this comment.
        """
        parent_comment = self.get_object()
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                author=request.user,
                article=parent_comment.article,
                reply_to=parent_comment
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)