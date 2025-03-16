from rest_framework import serializers
from taggit.serializers import TagListSerializerField, TaggitSerializer
from .models import Article

class ArticleSerializer(TaggitSerializer, serializers.ModelSerializer):
    tags = TagListSerializerField()
    author_username = serializers.ReadOnlyField(source='author.username')
    
    class Meta:
        model = Article
        fields = ('id', 'title', 'content', 'author', 'author_username', 'publication_date', 'updated_at', 'tags')
        read_only_fields = ('author', 'publication_date', 'updated_at')

    def create(self, validated_data):
        # The author will be set from the request user in the view
        return super().create(validated_data)