from django.urls import path
from .views import CommentViewSet

urlpatterns = [
    path('articles/<int:article_pk>/comments/', CommentViewSet.as_view({
        'get': 'list',
        'post': 'create'  # Make sure this line is present
    }), name='article-comments'),
    path('comments/<int:pk>/', CommentViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='comment-detail'),
]