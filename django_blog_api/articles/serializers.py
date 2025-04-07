from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer
from .models import Article

class ArticleSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    author_username = serializers.ReadOnlyField(source='author.username')
    
    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'author', 'author_username', 
                 'publication_date', 'updated_at', 'tags', 'status']
        read_only_fields = ['author', 'publication_date', 'updated_at']
    
    def create(self, validated_data):
        """
        Create and return a new Article instance, given the validated data.
        This method ensures the current user is set as the author.
        """
        # The author will be set by the view from the request.user
        user = self.context['request'].user
        validated_data['author'] = user
        return super().create(validated_data)