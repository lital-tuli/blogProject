from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import CommentViewSet

router = DefaultRouter()
router.register('comments', CommentViewSet, basename='comment')

urlpatterns = [
    # Article-specific comment endpoints
    path('articles/<int:article_pk>/comments/', CommentViewSet.as_view({
        'get': 'list',
        'post': 'create'  
    }), name='article-comments'),
 
    # Comment-specific endpoints
    path('comments/<int:pk>/', CommentViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='comment-detail'),
    
    # Reply endpoint
    path('comments/<int:pk>/reply/', CommentViewSet.as_view({
        'post': 'reply'
    }), name='comment-reply'),
]

# Add router URLs
urlpatterns += router.urls