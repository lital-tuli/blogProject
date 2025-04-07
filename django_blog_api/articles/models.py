from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager

class Article(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=120, unique=True)
    content = models.TextField()
    publish_date = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager()

    def __str__(self):
        return self.title