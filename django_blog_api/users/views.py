# django_blog_api/users/views.py
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
        'user': serializer.data,
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'message': 'Registration successful'
    }, status=status.HTTP_201_CREATED)