# django_blog_api/comments/serializers.py
from rest_framework import serializers
from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ('id', 'content', 'author', 'author_username', 'created_at', 'article', 'reply_to', 'replies')
        read_only_fields = ('author', 'created_at')
    
    def get_replies(self, obj):
        # Only fetch direct replies to this comment
        if 'request' in self.context:
            replies = obj.replies.all()
            serializer = CommentSerializer(replies, many=True, context=self.context)
            return serializer.data
        return []
    
    def validate_content(self, value):
        """
        Validates that the comment content doesn't contain inappropriate words.
        """
        inappropriate_words = ['spam', 'inappropriate', 'offensive']
        for word in inappropriate_words:
            if word in value.lower():
                raise serializers.ValidationError(
                    f"Comment contains inappropriate word: '{word}'"
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
        return value