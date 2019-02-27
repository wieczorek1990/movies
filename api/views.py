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
                return response.Response(data=serializer.data,
                                         status=status.HTTP_200_OK)

            else:
                return response.Response(data=movie_data,
                                         status=status.HTTP_400_BAD_REQUEST)
        else:
            return response.Response(data=serializer.data,
                                     status=status.HTTP_400_BAD_REQUEST)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = models.Comment.objects.all()
    serializer_class = serializers.CommentSerializer
    filter_class = filters.CommentFilter


class MovieCommentView(views.APIView):
    def get(self, request):
        serializer = serializers.MovieCommentRequestSerializer(
            data=request.query_params)

        if not serializer.is_valid():
            return response.Response(data=serializer.data,
                                     status=status.HTTP_400_BAD_REQUEST)

        comment_ids = models.Comment.objects.filter(
            created_at__gte=serializer.validated_data['from_date'],
            created_at__lte=serializer.validated_data['to_date'])\
            .values_list('id', flat=True)
        queryset = models.Movie.objects\
                               .annotate(total_comments=Count('comment'))\
                               .order_by('-total_comments')\
                               .filter(comment__id__in=comment_ids)\
                               .distinct()
        # The example provided included movies with total comments eq to 0
        queryset |= models.Movie.objects\
                                .annotate(total_comments=Count('comment'))\
                                .filter(total_comments=0)\
                                .distinct()

        current_rank = 1
        last_movie = None
        for movie in queryset:
            if last_movie is not None:
                if last_movie.total_comments != movie.total_comments:
                    current_rank += 1
            movie.rank = current_rank
            last_movie = movie

        serializer = serializers.MovieCommentResponseSerializer(
            queryset, many=True)

        return response.Response(status=status.HTTP_200_OK,
                                 data=serializer.data)
