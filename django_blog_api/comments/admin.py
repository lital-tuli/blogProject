from django.contrib import admin
from .models import Comment

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('truncated_content', 'author', 'article', 'created_at', 'reply_to')
    list_filter = ('created_at', 'author', 'article')
    search_fields = ('content', 'author__username', 'article__title')
    
    def truncated_content(self, obj):
        """Return truncated content for display in admin list view"""
        if len(obj.content) > 50:
            return f"{obj.content[:50]}..."
        return obj.content
    
    truncated_content.short_description = 'Content'