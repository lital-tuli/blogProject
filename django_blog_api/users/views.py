from rest_framework import viewsets, generics, permissions, status
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate
from .serializers import UserSerializer, UserRegistrationSerializer, LoginSerializer, ProfileSerializer
from .models import Profile
from utils.permissions import IsAdminUser

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for listing and retrieving users (admin only).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

class RegisterView(generics.CreateAPIView):
    """
    Register a new user and return JWT tokens.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Add user to regular users group
        users_group, _ = Group.objects.get_or_create(name='users')
        user.groups.add(users_group)
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    Authenticate user and return JWT tokens.
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(username=username, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            
            # Add user groups to token
            user_groups = [group.name for group in user.groups.all()]
            
            # Determine primary user group for frontend permissions
            user_group = "users"  # Default
            if "admin" in user_groups:
                user_group = "admin"
            elif "editors" in user_groups:
                user_group = "editors"
            
            return Response({
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'user_group': user_group
                },
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
    
    return Response(
        {'error': 'Invalid credentials'}, 
        status=status.HTTP_401_UNAUTHORIZED
    )

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_user_profile(request):
    """
    Get the profile for the authenticated user.
    """
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data)

@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([permissions.IsAuthenticated])
def profile_detail(request):
    """
    Get or update user profile.
    """
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
    
    if request.method == 'GET':
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)
    
    elif request.method in ['PUT', 'PATCH']:
        partial = request.method == 'PATCH'
        serializer = ProfileSerializer(profile, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def deactivate_account(request):
    """
    Deactivate the user's account
    """
    user = request.user
    user.is_active = False
    user.save()
    return Response(
        {'detail': 'Account deactivated successfully'}, 
        status=status.HTTP_200_OK
    )