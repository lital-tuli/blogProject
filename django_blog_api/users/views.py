from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from django.contrib.auth.models import User, Group
from .serializers import UserSerializer, LoginSerializer, UserRegistrationSerializer
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from utils.permissions import IsAdminUser

class UserViewSet(ViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = []

    def list(self, request):
        """
        Returns a list of users (admin only).
        """
        self.permission_classes = [IsAdminUser]
        self.check_permissions(request)  
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    @action(methods=['post'], detail=False)
    def register(self, request):
        """
        Register a new user and add them to the 'users' group.
        """
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Add user to the 'users' group
            users_group, _ = Group.objects.get_or_create(name='users')
            user.groups.add(users_group)
            
            # Generate JWT tokens
            token = RefreshToken.for_user(user)
            token['groups'] = [group.name for group in user.groups.all()]
            token['username'] = user.username
            
            return Response({
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "user_group": "users"  # Default group for new users
                },
                "refresh": str(token),
                "access": str(token.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False)
    def login(self, request):
        """
        Authenticate user and return JWT tokens.
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                request, 
                username=serializer.validated_data['username'],
                password=serializer.validated_data['password']
            )
            
            if user:
                token = RefreshToken.for_user(user)
                groups = [group.name for group in user.groups.all()]
                token['groups'] = groups
                token['username'] = user.username
                
                # Determine primary user group for frontend permission checks
                user_group = "users"  # Default
                if "admin" in groups:
                    user_group = "admin"
                elif "editors" in groups:
                    user_group = "editors"
                
                return Response({
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "user_group": user_group
                    },
                    "refresh": str(token),
                    "access": str(token.access_token),
                }, status=status.HTTP_200_OK)
                
        return Response({'message': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)