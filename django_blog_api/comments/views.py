from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
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
        elif self.action in ['create', 'reply']:
            return [permissions.IsAuthenticated()]
        elif self.action == 'destroy':
            return [permissions.IsAdminUser()]
        else:
            return [permissions.IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
        """
        Create a new comment for an article.
        """
        article_id = self.kwargs.get('article_pk')
        if not article_id:
            return Response(
                {"detail": "Article ID is required to create a comment."},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        article = get_object_or_404(Article, id=article_id)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check if this is a reply to another comment
        reply_to_id = request.data.get('reply_to')
        if reply_to_id:
            reply_to = get_object_or_404(Comment, id=reply_to_id)
            serializer.save(author=request.user, article=article, reply_to=reply_to)
        else:
            serializer.save(author=request.user, article=article)
            
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def get_queryset(self):
        """
        Filters comments by article if article_pk is provided in the URL.
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