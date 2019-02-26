from django.db import models

from api import fields


class Movie(models.Model):
    title = models.TextField()
    response = fields.JSONField()
    # other
    director = models.TextField()


class Comment(models.Model):
    body = models.TextField()
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
