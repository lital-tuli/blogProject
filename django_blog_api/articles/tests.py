from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User, Group
from articles.models import Article
from articles.serializers import ArticleSerializer
import json

class ArticleTests(TestCase):
    def setUp(self):
        # Create test users
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='adminpass123'
        )
        self.admin_user.is_staff = True
        self.admin_user.save()
        
        self.regular_user = User.objects.create_user(
            username='regular_test',
            email='regular@test.com',
            password='regularpass123'
        )
        
        # Create user groups
        self.editors_group, _ = Group.objects.get_or_create(name='editors')
        self.admin_user.groups.add(self.editors_group)
        
        # Create test article
        self.article = Article.objects.create(
            title='Test Article',
            content='This is a test article content',
            author=self.admin_user
        )
        self.article.tags.add('test')
        
        # Set up API client
        self.client = APIClient()
        
    def test_get_all_articles(self):
        """Test retrieving all articles"""
        response = self.client.get(reverse('article-list'))
        articles = Article.objects.all()
        serializer = ArticleSerializer(articles, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], serializer.data)
        
    def test_get_single_article(self):
        """Test retrieving a single article"""
        response = self.client.get(reverse('article-detail', kwargs={'pk': self.article.id}))
        serializer = ArticleSerializer(self.article)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
    
    def test_create_article_unauthenticated(self):
        """Test creating article without authentication fails"""
        data = {
            'title': 'New Test Article',
            'content': 'This is a new test article content',
            'tags': ['test', 'new']
        }
        response = self.client.post(
            reverse('article-list'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_article_authenticated_admin(self):
        """Test creating article with admin authentication succeeds"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'title': 'New Admin Article',
            'content': 'This is a new article by admin',
            'tags': ['test', 'admin']
        }
        response = self.client.post(
            reverse('article-list'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Article.objects.count(), 2)
        self.assertEqual(Article.objects.get(title='New Admin Article').author, self.admin_user)
    
    def test_create_article_regular_user(self):
        """Test creating article with regular user fails"""
        self.client.force_authenticate(user=self.regular_user)
        data = {
            'title': 'New Regular User Article',
            'content': 'This is a new article by regular user',
            'tags': ['test', 'regular']
        }
        response = self.client.post(
            reverse('article-list'),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_article_admin(self):
        """Test updating article by admin succeeds"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'title': 'Updated Test Article',
            'content': 'This is updated test article content',
            'tags': ['test', 'updated']
        }
        response = self.client.put(
            reverse('article-detail', kwargs={'pk': self.article.id}),
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.article.refresh_from_db()
        self.assertEqual(self.article.title, 'Updated Test Article')
    
    def test_delete_article_admin(self):
        """Test deleting article by admin succeeds"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(
            reverse('article-detail', kwargs={'pk': self.article.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Article.objects.count(), 0)
    
    def test_filter_articles_by_tag(self):
        """Test filtering articles by tag"""
        Article.objects.create(
            title='Another Test Article',
            content='This is another test article content',
            author=self.admin_user
        )
        response = self.client.get(f"{reverse('article-list')}?tag=test")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  