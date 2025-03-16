from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from articles.models import Article
from .models import Comment
from .serializers import CommentSerializer
from core.permissions import IsAdminOrAuthorOrReadOnly

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAdminOrAuthorOrReadOnly]
    
    def perform_create(self, serializer):
        article_id = self.kwargs.get('article_pk')
        article = get_object_or_404(Article, id=article_id)
        serializer.save(author=self.request.user, article=article)
    
    def get_queryset(self):
        article_id = self.kwargs.get('article_pk')
        if article_id:
            return Comment.objects.filter(article__id=article_id)
        return Comment.objects.all()