from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
import json

class UserAuthTests(TestCase):
    def setUp(self):
        # Create test user
        self.existing_user = User.objects.create_user(
            username='existing_user',
            email='existing@test.com',
            password='existingpass123'
        )
        
        # Set up API client
        self.client = APIClient()
        
    def test_user_registration(self):
        """Test user registration with valid data"""
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password': 'NewUserPass123'
        }
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
        self.assertEqual(response.data['user']['username'], 'newuser')
        self.assertEqual(User.objects.count(), 2)
    
    def test_user_registration_weak_password(self):
        """Test user registration with weak password fails"""
        url = reverse('register')
        data = {
            'username': 'weakuser',
            'email': 'weak@test.com',
            'password': '12345'  # Too simple
        }
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)  # No new user created
    
    def test_user_registration_duplicate_username(self):
        """Test user registration with duplicate username fails"""
        url = reverse('register')
        data = {
            'username': 'existing_user',  # Already exists
            'email': 'new@test.com',
            'password': 'NewUserPass123'
        }
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)  # No new user created
    
    def test_token_obtain(self):
        """Test obtaining JWT token with valid credentials"""
        url = reverse('token_obtain_pair')
        data = {
            'username': 'existing_user',
            'password': 'existingpass123'
        }
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.data)
        self.assertTrue('refresh' in response.data)
    
    def test_token_obtain_invalid_credentials(self):
        """Test obtaining JWT token with invalid credentials fails"""
        url = reverse('token_obtain_pair')
        data = {
            'username': 'existing_user',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_token_refresh(self):
        """Test refreshing JWT token"""
        # First, obtain a token
        obtain_url = reverse('token_obtain_pair')
        obtain_data = {
            'username': 'existing_user',
            'password': 'existingpass123'
        }
        obtain_response = self.client.post(obtain_url, data=json.dumps(obtain_data), content_type='application/json')
        refresh_token = obtain_response.data['refresh']
        
        # Then, try to refresh it
        refresh_url = reverse('token_refresh')
        refresh_data = {'refresh': refresh_token}
        refresh_response = self.client.post(refresh_url, data=json.dumps(refresh_data), content_type='application/json')
        
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in refresh_response.data)