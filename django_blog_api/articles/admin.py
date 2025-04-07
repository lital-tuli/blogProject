from django.contrib import admin
from .models import Article

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publication_date', 'status')
    list_filter = ('status', 'publication_date', 'author')
    search_fields = ('title', 'content', 'author__username')
    readonly_fields = ('publication_date', 'updated_at')
    # Remove filter_horizontal for tags since it uses a custom relationship model