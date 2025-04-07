from django.db import models
from django.core.validators import MaxLengthValidator, MinLengthValidator
from articles.models import Article
from django.contrib.auth.models import User

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(
        validators=[
            MinLengthValidator(5),
            MaxLengthValidator(1000)
        ]
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    publish_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    reply_to = models.ForeignKey('self', on_delete=models.CASCADE, default=None, null=True, blank=True, related_name='replies')

    def __str__(self):
        return f'Comment by {self.author.username} on {self.article.title}'