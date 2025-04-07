from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User, Group
from .serializers import UserSerializer, ProfileSerializer
from .models import Profile
from django.shortcuts import get_object_or_404
from core.utils import error_response
from django.db import transaction
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle, ScopedRateThrottle


class AuthRateThrottle(ScopedRateThrottle):
    scope = 'auth'

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile_detail(request, pk=None):
    
  
    # If no pk is provided, use the current user's profile
    if pk is None:
        profile = request.user.profile
    else:
        profile = get_object_or_404(Profile, user__id=pk)
    
    if request.method == 'GET':
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)
    
    # Only allow updating your own profile
    if request.method == 'PUT':
        if profile.user != request.user:
            return error_response(
                "You can only update your own profile.",
                status.HTTP_403_FORBIDDEN
            )
        
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(
                "Invalid profile data", 
                status.HTTP_400_BAD_REQUEST,
                serializer.errors
            )
            
        serializer.save()
        return Response(serializer.data)

class RegisterView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]
    
    # In users/views.py - RegisterView
    @transaction.atomic
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                "Invalid registration data", 
                status.HTTP_400_BAD_REQUEST,
                serializer.errors
            )
            
        user = serializer.save()
        
        # Add user to the 'users' group
        users_group, _ = Group.objects.get_or_create(name='users')
        user.groups.add(users_group)
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
    'user': {
        'id': user.id,
        'username': user.username,
        'email': user.email,
    },
    'refresh': str(refresh),
    'access': str(refresh.access_token),
    'message': 'Registration successful'
}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deactivate_account(request):
    """
    Deactivate the current user's account.
    This doesn't delete the account but makes it inactive.
    """
    user = request.user
    
    # Require password confirmation for security
    password = request.data.get('password', '')
    if not user.check_password(password):
        return error_response(
            "Current password is incorrect", 
            status.HTTP_400_BAD_REQUEST
        )
    
    # Deactivate the account
    user.is_active = False
    user.save()
    
    # Blacklist any existing tokens
    if 'rest_framework_simplejwt.token_blacklist' in settings.INSTALLED_APPS:
        # Get user's refresh tokens
        from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
        outstanding_tokens = OutstandingToken.objects.filter(user=user)
        for token in outstanding_tokens:
            if not token.blacklisted:
                BlacklistedToken.objects.create(token=token)
    
    return Response({
        "message": "Your account has been deactivated. You can contact support to reactivate it."
    }, status=status.HTTP_200_OK)