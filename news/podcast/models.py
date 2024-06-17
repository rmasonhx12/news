from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=255)
    link = models.URLField()
    description = models.TextField()
    transcript = models.TextField()
    audio = models.BinaryField()

