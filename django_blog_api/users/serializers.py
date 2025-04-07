from rest_framework.serializers import ModelSerializer, Serializer, CharField
from django.contrib.auth.models import User

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(Serializer):
    username = CharField()
    password = CharField(write_only=True)

class UserRegistrationSerializer(ModelSerializer):
    """Serializer for user registration with password confirmation."""
    password_confirm = CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}
        
    def validate(self, data):
        """Validate that passwords match."""
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError("Passwords don't match")
        return data
        
    def create(self, validated_data):
        """Create a new user instance."""
        # Remove the password_confirm field as it's not needed in User creation
        validated_data.pop('password_confirm', None)
        
        user = User.objects.create_user(**validated_data)
        return user