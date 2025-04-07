from django.contrib import admin
from .models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publish_date')
    list_filter = ('publish_date', 'author')
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('publish_date',)
    filter_horizontal = ('tags',)