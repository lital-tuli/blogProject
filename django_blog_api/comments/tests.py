from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from articles.models import Article
from comments.models import Comment
import json

class CommentTests(TestCase):
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
        
        # Create test article
        self.article = Article.objects.create(
            title='Test Article',
            content='This is a test article content',
            author=self.admin_user
        )
        
        # Create test comment
        self.comment = Comment.objects.create(
            article=self.article,
            content='This is a test comment',
            author=self.regular_user
        )
        
        # Set up API client
        self.client = APIClient()
        
    def test_get_all_comments_for_article(self):
        """Test retrieving all comments for an article"""
        url = reverse('article-comments', kwargs={'article_pk': self.article.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
    def test_create_comment_unauthenticated(self):
        """Test creating comment without authentication fails"""
        url = reverse('article-comments', kwargs={'article_pk': self.article.id})
        data = {'content': 'New anonymous comment'}
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_comment_authenticated(self):
        """Test creating comment with authentication succeeds"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('article-comments', kwargs={'article_pk': self.article.id})
        data = {'content': 'New authenticated comment'}
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)
    
    def test_update_own_comment(self):
        """Test updating own comment succeeds"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('comment-detail', kwargs={'pk': self.comment.id})
        data = {'content': 'Updated comment content'}
        response = self.client.put(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.content, 'Updated comment content')
    
    def test_update_other_user_comment(self):
        """Test updating another user's comment fails"""
        # Create another user and authenticate as them
        other_user = User.objects.create_user(
            username='other_test',
            email='other@test.com',
            password='otherpass123'
        )
        self.client.force_authenticate(user=other_user)
        
        url = reverse('comment-detail', kwargs={'pk': self.comment.id})
        data = {'content': 'Attempt to update another user\'s comment'}
        response = self.client.put(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
    def test_delete_comment_admin(self):
        """Test admin can delete any comment"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('comment-detail', kwargs={'pk': self.comment.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Comment.objects.count(), 0)
    
    def test_delete_comment_author(self):
        """Test comment author cannot delete their comment (only admins can)"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('comment-detail', kwargs={'pk': self.comment.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Comment.objects.count(), 1)
    
    def test_create_reply_to_comment(self):
        """Test creating a reply to a comment"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('article-comments', kwargs={'article_pk': self.article.id})
        data = {
            'content': 'This is a reply to the comment',
            'reply_to': self.comment.id
        }
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Comment.objects.count(), 2)
        self.assertEqual(Comment.objects.get(id=response.data['id']).reply_to.id, self.comment.id)