from rest_framework import serializers
from .models import Comment
from articles.models import Article

class CommentSerializer(serializers.ModelSerializer):
    author_username = serializers.ReadOnlyField(source='author.username')
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'author_username', 'article', 
                 'created_at', 'reply_to', 'replies']
        read_only_fields = ['author', 'created_at', 'article']
    
    def get_replies(self, obj):
        """Return serialized replies for this comment"""
        # Only include direct replies to avoid recursion issues
        replies = obj.replies.all()
        if replies:
            return CommentSerializer(replies, many=True, context=self.context).data
        return []
    
    def create(self, validated_data):
        """
        Create and return a new Comment instance, given the validated data.
        This method ensures the current user is set as the author.
        """
        # The author will be set by the view
        user = self.context['request'].user
        validated_data['author'] = user
        
        # The article_id comes from the URL
        article_id = self.context['view'].kwargs.get('article_id')
        if article_id:
            try:
                article = Article.objects.get(id=article_id)
                validated_data['article'] = article
            except Article.DoesNotExist:
                raise serializers.ValidationError("Article not found")
        
        return super().create(validated_data)
    
    def validate_reply_to(self, value):
        """
        Ensure the reply_to comment belongs to the same article.
        """
        if value:
            article_id = self.context['view'].kwargs.get('article_id')
            if article_id and value.article.id != int(article_id):
                raise serializers.ValidationError(
                    "You can only reply to comments from the same article."
                )
        return value