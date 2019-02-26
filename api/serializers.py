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


class MovieCommentRequestSerializer(serializers.Serializer):
    from_date = serializers.DateTimeField()
    to_date = serializers.DateTimeField()


class MovieCommentResponseSerializer(serializers.Serializer):
    movie_id = serializers.IntegerField(source='id')
    total_comments = serializers.IntegerField()
    rank = serializers.IntegerField()
