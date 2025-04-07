from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, get_user_profile, profile_detail, deactivate_account, UserViewSet, login_view

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', login_view, name='login'),
    path('user/', get_user_profile, name='user-profile'),
    path('profile/', profile_detail, name='current-user-profile'),
    path('deactivate/', deactivate_account, name='deactivate-account'),
    path('', include(router.urls)),
]