# django_blog_api/comments/serializers.py
from rest_framework import serializers
from .models import Comment
from django.utils.html import strip_tags

class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Comment model.
    
    Includes additional fields:
    - author_username: The username of the comment author
    - author_id: The ID of the comment author
    - replies: Nested comments (replies) to this comment
    """
    author_username = serializers.ReadOnlyField(source='author.username')
    author_id = serializers.ReadOnlyField(source='author.id')
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ('id', 'content', 'author', 'author_id', 'author_username', 
                  'created_at', 'article', 'reply_to', 'replies')
        read_only_fields = ('author', 'created_at')
    
    def get_replies(self, obj):
        """Get replies to this comment"""
        replies = Comment.objects.filter(reply_to=obj)
        if replies.exists():
            return CommentSerializer(replies, many=True, context=self.context).data
        return []
    
    def validate_content(self, value):
        """
        Validates that the comment content is appropriate and properly formatted.
        """
        # Check for inappropriate words
        inappropriate_words = ['spam', 'inappropriate', 'offensive']
        for word in inappropriate_words:
            if word in value.lower():
                raise serializers.ValidationError(
                    f"Comment contains inappropriate word: '{word}'"
                )
                
        # Check for HTML tags (simple security measure)
        if value != strip_tags(value):
            raise serializers.ValidationError(
                "Comment cannot contain HTML tags"
            )
            
        # Check length (though model validator should catch this too)
        if len(value) < 2:
            raise serializers.ValidationError(
                "Comment must be at least 2 characters long"
            )
            
        return value
    
    def validate_reply_to(self, value):
        """
        Validates that the reply_to comment belongs to the same article.
        """
        if value and 'article' in self.initial_data:
            article_id = self.initial_data.get('article')
            if value.article.id != int(article_id):
                raise serializers.ValidationError(
                    "Reply must be to a comment on the same article"
                )
                
        # Prevent nested replies beyond a certain depth
        if value and value.reply_to is not None:
            raise serializers.ValidationError(
                "Nested replies beyond one level are not allowed"
            )
                
        return value
        
    def validate(self, data):
        """
        Perform cross-field validation.
        """
        # Additional validation logic can be added here
        return data