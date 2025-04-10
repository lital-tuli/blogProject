from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from taggit.managers import TaggableManager

class Article(models.Model):
    title = models.CharField(
        max_length=200, 
        unique=True,
        validators=[MinLengthValidator(5)],
        help_text="Title must be unique and at least 5 characters long"
    )
    content = models.TextField(
        validators=[MinLengthValidator(10)],
        help_text="Article content must be at least 10 characters long"
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='articles',
        help_text="The user who created this article"
    )
    publication_date = models.DateTimeField(
        auto_now_add=True,
        help_text="Date and time when the article was published"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Date and time when the article was last updated"
    )
    tags = TaggableManager(
        blank=True,
        help_text="Optional tags to categorize the article"
    )
    status = models.CharField(
        max_length=10,
        choices=[
            ('draft', 'Draft'),
            ('published', 'Published'),
            ('archived', 'Archived')
        ],
        default='draft',
        help_text="Publication status of the article"
    )

    class Meta:
        ordering = ['-publication_date']

    def __str__(self):
        return self.title