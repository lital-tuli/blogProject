from rest_framework import viewsets, filters, permissions, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Article
from .serializers import ArticleSerializer
from utils.permissions import IsAdminUser, IsAdminOrEditorUser

class ArticleViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing articles.
    """
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tags__name', 'author__username', 'status']
    search_fields = ['title', 'content', 'tags__name', 'author__username']
    ordering_fields = ['publication_date', 'title']
    ordering = ['-publication_date']  # Default ordering
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [permissions.AllowAny]
        elif self.action == 'create':
            permission_classes = [IsAdminOrEditorUser]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAdminOrEditorUser]
        elif self.action == 'destroy':
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        """
        Save the author as the current user when creating an article.
        """
        serializer.save(author=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        """
        Override destroy method to return a custom success message.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {'message': 'Article deleted successfully'}, 
            status=status.HTTP_200_OK
        )