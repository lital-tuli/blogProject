
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, MethodNotAllowed
from .models import Comment
from .serializers import CommentSerializer
from articles.models import Article
from utils.permissions import IsAdminUser, IsOwner, AnyUser

class CommentViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing comments.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    def get_queryset(self):
        """
        Filter comments based on article_id if provided in the URL.
        Returns only root comments (not replies) for better organization.
        """
        article_id = self.kwargs.get('article_id')
        if article_id:
            if not Article.objects.filter(id=article_id).exists():
                raise NotFound(detail="Article not found.")
            return Comment.objects.filter(article_id=article_id, reply_to=None)
        return Comment.objects.filter(reply_to=None)
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions for this view.
        """
        if self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, AnyUser]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsOwner]
        elif self.action == 'destroy':
            permission_classes = [permissions.IsAuthenticated, IsOwner]  # Allow authors to delete their own comments
        else:  # 'list', 'retrieve'
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        """
        Create a new comment for a specific article.
        """
        article_id = kwargs.get('article_id')
        if not article_id:
            return Response(
                {"error": "Article ID is required to create a comment."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            article = Article.objects.get(id=article_id)
        except Article.DoesNotExist:
            raise NotFound(detail="Article not found.")
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author=request.user, article=article)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """
        Disallow full update (PUT method). Only partial updates allowed.
        """
        if request.method == 'PUT':
            raise MethodNotAllowed("PUT", detail="Full update is not allowed. Use PATCH instead.")
        return self.partial_update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Partially update a comment (only content field allowed).
        """
        instance = self.get_object()
        data = request.data
        
        # Check if there are any fields other than 'content'
        if set(data.keys()) - {'content'}:
            return Response(
                {"detail": "Only 'content' field is allowed to be updated."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)