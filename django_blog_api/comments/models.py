
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from articles.models import Article

class Comment(models.Model):
    """
    Model representing a comment on an article.
    
    Comments can be made on articles or as replies to other comments.
    Each comment has a content, author, and creation timestamp.
    Comments are ordered chronologically.
    """
    article = models.ForeignKey(
        Article, 
        on_delete=models.CASCADE, 
        related_name='comments',
        help_text="The article this comment belongs to"
    )
    content = models.TextField(
        validators=[MinLengthValidator(2)],
        help_text="Comment content must be at least 2 characters long"
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='comments',
        help_text="The user who created this comment"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when the comment was created"
    )
    reply_to = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='replies',
        help_text="The parent comment this comment is replying to, if any"
    )

    def __str__(self):
        return f"Comment by {self.author.username} on {self.article.title}"

    class Meta:
        ordering = ['created_at']