from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator, FileExtensionValidator
from taggit.managers import TaggableManager


class Article(models.Model):
    """
    Model representing a blog article.
    
    Each article has a title, content, author, and optional tags.
    Articles are ordered by publication date with newest first.
    """
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
image = models.ImageField(
    upload_to='article_images/',
    validators=[
        FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif']),
    ],
    null=True,
    blank=True
)
tags = TaggableManager(
    blank=True,
    help_text="Optional tags to categorize the article"
)
featured_image = models.ImageField(
    upload_to='article_images/%Y/%m/', 
    null=True, 
    blank=True,
    validators=[
        FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif']),
    ],
    help_text="Featured image for the article (max 5MB, jpg/png/gif only)"
)

STATUS_CHOICES = (
    ('draft', 'Draft'),
    ('published', 'Published'),
    ('archived', 'Archived'),
)
status = models.CharField(
    max_length=10,
    choices=STATUS_CHOICES,
    default='draft',
    help_text="Publication status of the article"
)

def __str__(self):
    return f"{self.title} by {self.author.username}"

def get_tags_display(self):
    return ', '.join(tag.name for tag in self.tags.all())

class Meta:
    ordering = ['-publication_date']

def clean(self):
    super().clean()
    if self.featured_image:
        if self.featured_image.size > settings.MAX_IMAGE_SIZE:
            raise ValidationError({
                'featured_image': f'Image size must not exceed {settings.MAX_IMAGE_SIZE // (1024 * 1024)}MB'
            })

