from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomApiRootView
from rest_framework_simplejwt.views import TokenRefreshView
from articles.views import ArticleViewSet
from comments.views import CommentViewSet
from users.views import UserViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    
    # API authentication URLs
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Custom API root view
    path('api/', CustomApiRootView.as_view(), name='api-root'),
    
    # Include the router URLs
    path('api/', include(router.urls)),
    
    # Article comments endpoint
    path('api/articles/<int:article_id>/comments/', 
         CommentViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='article-comments'),
    
    # User-related endpoints
    path('api/users/', UserViewSet.as_view({'get': 'list'}), name='users'),
    path('api/register/', UserViewSet.as_view({'post': 'register'}), name='register'),
    path('api/login/', UserViewSet.as_view({'post': 'login'}), name='login'),
    
    # DRF browsable API authentication (for development)
    path('api-auth/', include('rest_framework.urls')),
]