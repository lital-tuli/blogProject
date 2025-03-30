from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action  # Add this import
from django.shortcuts import get_object_or_404
from articles.models import Article
from .models import Comment
from .serializers import CommentSerializer

class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for handling comment operations.
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
            return [permissions.AllowAny()]
        elif self.action == 'create':
            return [permissions.IsAuthenticated()]
        elif self.action == 'destroy':
            return [permissions.IsAdminUser()]
        else:
            return [permissions.IsAuthenticated()]
    
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
    
    def get_queryset(self):
        """
        Filters comments by article if article_pk is provided in the URL.
        """
        article_id = self.kwargs.get('article_pk')
        if article_id:
            return Comment.objects.filter(article__id=article_id)
        return Comment.objects.all()
    
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