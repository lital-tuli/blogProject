from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer
from .models import Article
from comments.models import Comment

class ArticleSerializer(TaggitSerializer, serializers.ModelSerializer):
    """
    Serializer for the Article model.
    
    Includes tags using TagListSerializerField and adds additional fields:
    - author_username: The username of the article author
    - comment_count: The number of comments on this article
    """
    tags = TagListSerializerField()
    author_username = serializers.ReadOnlyField(source='author.username')
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Article
        fields = ('id', 'title', 'content', 'author', 'author_username', 
                  'publication_date', 'updated_at', 'tags', 'comment_count')
        read_only_fields = ('author', 'publication_date', 'updated_at')

    def get_comment_count(self, obj):
        """Returns the number of comments on this article."""
        return obj.comments.count()
        
    def validate_title(self, value):
        """
        Validates that the title doesn't contain inappropriate content.
        
        This is a simplified example. In a real app, you might use more 
        sophisticated filtering.
        """
        inappropriate_words = ['spam', 'inappropriate', 'offensive']
        for word in inappropriate_words:
            if word in value.lower():
                raise serializers.ValidationError(
                    f"Title contains inappropriate word: '{word}'"
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
                    "Title and content cannot be identical"
                )
        return data