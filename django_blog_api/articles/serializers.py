from rest_framework.serializers import ModelSerializer, SerializerMethodField, HiddenField
from rest_framework.serializers import CurrentUserDefault
from taggit.serializers import TaggitSerializer, TagListSerializerField
from .models import Article

class ArticleSerializer(TaggitSerializer, ModelSerializer):
    tags = TagListSerializerField()
    author = HiddenField(default=CurrentUserDefault())
    author_id = SerializerMethodField()
    author_name = SerializerMethodField()
    
    class Meta:
        model = Article
        fields = '__all__'

    def get_author_id(self, obj):
        return obj.author.id
    
    def get_author_name(self, obj):
        return obj.author.username