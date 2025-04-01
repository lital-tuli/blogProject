from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ArticleViewSet

# Create a router and register our viewset
router = DefaultRouter()
router.register('articles', ArticleViewSet, basename='article')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]