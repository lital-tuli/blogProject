from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from articles.models import Article

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(validators=[MinLengthValidator(2)])
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)
    reply_to = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')

    def __str__(self):
        return f"Comment by {self.author.username} on {self.article.title}"

    class Meta:
        ordering = ['created_at']