from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from articles.models import Article
from .models import Comment
from .serializers import CommentSerializer

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
            permission_classes = [permissions.AllowAny]
        elif self.action == 'create':
            # Only authenticated users can create comments
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'destroy':
            # Only admin users can delete comments
            permission_classes = [permissions.IsAdminUser]
        else:
            # For update/partial_update, use IsAuthenticated
            # We'll check author in perform_update
            permission_classes = [permissions.IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        Sets the author to the current user and the article based on URL parameter.
        """
        article_id = self.kwargs.get('article_pk')
        article = get_object_or_404(Article, id=article_id)
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
        """
        article_id = self.kwargs.get('article_pk')
        if article_id:
            return Comment.objects.filter(article__id=article_id)
        return Comment.objects.all()