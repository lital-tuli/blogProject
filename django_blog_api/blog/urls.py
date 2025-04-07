from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

# Import views separately to avoid circular imports
from blog.views import CustomApiRootView
from articles.views import ArticleViewSet
from comments.views import CommentViewSet
from users.views import login_view, RegisterView, UserViewSet

# Create a router and register our viewsets
router = DefaultRouter()
router.register(r'articles', ArticleViewSet, basename='article')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),
    
    # API authentication URLs
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Custom API root view
    path('api/', CustomApiRootView.as_view(), name='api-root'),
    
    # Include the router URLs
    path('api/', include(router.urls)),
    
    # Authentication endpoints
    path('api/login/', login_view, name='login'),
    path('api/register/', RegisterView.as_view(), name='register'),
    
    # Article comments endpoint
    path('api/articles/<int:article_id>/comments/', 
         CommentViewSet.as_view({'get': 'list', 'post': 'create'}), 
         name='article-comments'),
    
    # DRF browsable API authentication (for development)
    path('api-auth/', include('rest_framework.urls')),
]