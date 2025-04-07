from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault, SerializerMethodField
from .models import Comment
from utils.fetch_article import ArticleFromURL

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True, default=CurrentUserDefault())
    author_name = SerializerMethodField()
    article = serializers.PrimaryKeyRelatedField(read_only=True, default=ArticleFromURL())
    reply_to = serializers.PrimaryKeyRelatedField(queryset=Comment.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Comment
        fields = '__all__'

    def get_author_name(self, obj):
        return obj.author.username

    def get_fields(self):
        """Dynamically filter reply_to queryset to only show comments from the same article."""
        fields = super().get_fields()
        article_id = self.context.get('view', {}).kwargs.get('article_id')
        if article_id:
            try:
                article_id = int(article_id)  
                fields['reply_to'].queryset = Comment.objects.filter(article_id=article_id)
            except ValueError:
                pass  
        return fields

    def validate(self, data):
        """
        Custom validation to check if parent_comment belongs to the same article.
        """
        article_id = self.context.get('view', {}).kwargs.get('article_id')
        if not article_id:
            raise serializers.ValidationError("Article ID is required")
        reply_comment = data.get('reply_to')  

        if reply_comment:
            reply_comment_id = reply_comment.id
            reply_comment_article = Comment.objects.filter(id=reply_comment_id).values_list('article', flat=True).first()

            if reply_comment_article != article_id:
                raise serializers.ValidationError("You can only reply to comments from the same article.")

        return data