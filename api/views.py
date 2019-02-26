import requests
from django.conf import settings
from django.db.models import Count
from rest_framework import filters as rest_framework_filters
from rest_framework import views
from rest_framework import viewsets
from rest_framework import response
from rest_framework import status

from api import filters
from api import models
from api import serializers


class MovieViewSet(viewsets.ModelViewSet):
    queryset = models.Movie.objects.all()
    serializer_class = serializers.MovieSerializer
    filter_backends = (rest_framework_filters.OrderingFilter,)
    ordering_fileds = '__all__'

    @staticmethod
    def get_omdb_api_url(title):
        return 'http://www.omdbapi.com/?apikey={}&t={}'.format(
            settings.OMDB_API_KEY, title)

    def create(self, request):
        serializer = serializers.MovieTitleSerializer(data=request.data)
        if serializer.is_valid():
            title = serializer.validated_data['title']
            url = self.get_omdb_api_url(title)
            movie_response = requests.get(url)
            movie_data = movie_response.json()
            if movie_data['Response'] == 'True':
                movie = models.Movie(title=title,
                                     response=movie_data,
                                     director=movie_data['Director'])
                movie.save()
                serializer = serializers.MovieSerializer(instance=movie)
                return response.Response(status=status.HTTP_200_OK,
                                        data=serializer.data)
            else:
                return response.Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return response.Response(status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = models.Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    filter_class = filters.CommentFilter


class MovieCommentView(views.APIView):
    def get(self, request):
        queryset = models.Movie.objects\
                               .annotate(total_comments=Count('comment'))\
                               .order_by('-total_comments')

        current_rank = 0
        last_movie = None
        for index, movie in enumerate(queryset):
            if last_movie is None:
                current_rank += 1
            else:
                if last_movie.total_comments != movie.total_comments:
                    current_rank += 1
            movie.rank = current_rank
            last_movie = movie

        serializer = serializers.MovieCommentResponseSerializer(
            queryset, many=True)

        return response.Response(status=status.HTTP_200_OK,
                                 data=serializer.data)
