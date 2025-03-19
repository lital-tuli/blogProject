from rest_framework import viewsets, filters, permissions
from django_filters.rest_framework import DjangoFilterBackend
from .models import Article
from .serializers import ArticleSerializer
from core.permissions import IsAdminUserOrReadOnly

class ArticleViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAdminUserOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tags__name', 'author__username']
    search_fields = ['title', 'content', 'tags__name', 'author__username']
    ordering_fields = ['publication_date', 'title']
    ordering = ['-publication_date']
    
    def get_queryset(self):
        queryset = Article.objects.all()
        
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
        serializer.save(author=self.request.user)