import requests
from django.conf import settings
from rest_framework import viewsets
from rest_framework import response
from rest_framework import status

from api import models
from api import serializers


class MovieViewSet(viewsets.ModelViewSet):
    queryset = models.Movie.objects.all()
    serializer_class = serializers.MovieSerializer

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
