from rest_framework import serializers

from api import models


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Movie
        fields = ('title', 'response', 'director')


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Comment
        fields = ('body', 'movie')


class MovieTitleSerializer(serializers.Serializer):
    title = serializers.CharField()
