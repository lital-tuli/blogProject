from rest_framework import serializers
from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    
    class Meta:
        model = Comment
        fields = ('id', 'article', 'content', 'author', 'author_username', 'created_at', 'reply_to')
        read_only_fields = ('author', 'created_at')