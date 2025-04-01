# django_blog_api/articles/serializers.py
from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer
from .models import Article
from django.utils.html import strip_tags

class ArticleSerializer(TaggitSerializer, serializers.ModelSerializer):
    """
    Serializer for the Article model.
    
    Includes tags using TagListSerializerField and adds additional fields:
    - author_username: The username of the article author
    - author_id: The ID of the article author
    - comment_count: The number of comments on this article
    """
    tags = TagListSerializerField()
    author_username = serializers.ReadOnlyField(source='author.username')
    author_id = serializers.ReadOnlyField(source='author.id')
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = ('id', 'title', 'content', 'author', 'author_id', 'author_username', 
                  'publication_date', 'updated_at', 'tags', 'comment_count')
        read_only_fields = ('author', 'publication_date', 'updated_at')

    def get_comment_count(self, obj):
        """Returns the number of comments on this article."""
        return getattr(obj, 'comment_count', obj.comments.count())
        
    def validate_title(self, value):
        """
        Validates that the title doesn't contain inappropriate content and is properly formatted.
        """
        # Check for inappropriate content
        inappropriate_words = ['spam', 'inappropriate', 'offensive']
        for word in inappropriate_words:
            if word in value.lower():
                raise serializers.ValidationError(
                    f"Title contains inappropriate word: '{word}'"
                )
                
        # Check for HTML tags (simple security measure)
        if value != strip_tags(value):
            raise serializers.ValidationError(
                "Title cannot contain HTML tags"
            )
            
        # Check length again (though model validator should catch this too)
        if len(value) < 5:
            raise serializers.ValidationError(
                "Title must be at least 5 characters long"
            )
            
        return value
    
    def validate_content(self, value):
        """
        Validates the article content.
        """
        # Check for inappropriate content
        inappropriate_words = ['spam', 'inappropriate', 'offensive']
        for word in inappropriate_words:
            if word in value.lower():
                raise serializers.ValidationError(
                    f"Content contains inappropriate word: '{word}'"
                )
                
        # Check length again (though model validator should catch this too)
        if len(value) < 10:
            raise serializers.ValidationError(
                "Content must be at least 10 characters long"
            )
            
        return value
    
    def validate(self, data):
        """
        Performs validation on the entire data object.
        
        Checks that the title and content are different.
        """
        if 'title' in data and 'content' in data:
            if data['title'] == data['content']:
                raise serializers.ValidationError(
                    {"non_field_errors": ["Title and content cannot be identical"]}
                )
                
            # Check if title is contained completely within content
            if data['title'] in data['content']:
                # This is just a warning, not an error
                pass
                
        return data