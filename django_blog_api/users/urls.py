from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, get_user_profile, profile_detail

urlpatterns = [
    
    path('register/', RegisterView.as_view(), name='register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    
    path('user/', get_user_profile, name='user-profile'),
    path('profile/', profile_detail, name='current-user-profile'),
    path('profile/<int:pk>/', profile_detail, name='user-profile-detail'),
]