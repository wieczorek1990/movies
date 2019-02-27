import json
from datetime import datetime, timedelta

import httpretty
from django.conf import settings
from django.test import TransactionTestCase
from django.test.utils import override_settings
from rest_framework import status

from api import models
from api import responses


class MovieTestCase(TransactionTestCase):
    @override_settings(OMDB_API_KEY='ac8abfb3')
    @httpretty.activate
    def test_post_movie(self):
        uri = 'http://www.omdbapi.com/?apikey={}&t={}'.format(
                settings.OMDB_API_KEY, 'Kill Bill')
        httpretty.register_uri(httpretty.GET,
                               uri,
                               json.dumps(responses.OMDB_API_RESPONSE))
        response = self.client.post('/movies/',
                                    {'title': 'Kill Bill'},
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_movies(self):
        models.Movie(title='Kill Bill',
                     response='',
                     director='Quentin Tarantino').save()
        response = self.client.get('/movies/')
        self.assertEqual(response.json(), [
            {'title': 'Kill Bill',
             'response': '',
             'director': 'Quentin Tarantino'}])
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CommentTestCase(TransactionTestCase):
    def setUp(self):
        self.movie = models.Movie(title='Kill Bill',
                                  response='',
                                  director='Quentin Tarantino')
        self.movie.save()

    def test_post_comment(self):
        response = self.client.post('/comments/',
                                    {'body': 'Exciting.',
                                     'movie': self.movie.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json(), {'body': 'Exciting.',
                                           'movie': self.movie.id})

    def test_get_comments(self):
        models.Comment(movie=self.movie, body='Exciting.').save()
        response = self.client.get('/comments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(),
                         [{'body': 'Exciting.', 'movie': self.movie.id}])

    def test_get_comments_by_movie_id(self):
        models.Comment(movie=self.movie, body='Exciting.').save()
        response = self.client.get(
            '/comments/?movie={}'.format(self.movie.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(),
                         [{'body': 'Exciting.', 'movie': self.movie.id}])


class MovieCommentTestCase(TransactionTestCase):
    def test_get_top(self):
        movie_data = [{'title': 'Kill Bill',
                       'response': '',
                       'director': 'Quentin Tarantino'},
                      {'title': 'Kill Bill 2',
                       'response': '',
                       'director': 'Quentin Tarantino'},
                      {'title': 'Kill Bill 3',
                       'response': '',
                       'director': 'Quentin Tarantino'},
                      {'title': 'Kill Bill 4',
                       'response': '',
                       'director': 'Quentin Tarantino'}]
        movies = []
        for movie in movie_data:
            movie = models.Movie(title=movie['title'],
                                 response=movie['response'],
                                 director=movie['director'])
            movie.save()
            movies.append(movie)
        comment_data = [{'movie': movies[0], 'body': 'Exciting.'},
                        {'movie': movies[0], 'body': 'Exciting.'},
                        {'movie': movies[0], 'body': 'Exciting.'},
                        {'movie': movies[0], 'body': 'Exciting.'},
                        {'movie': movies[1], 'body': 'Exciting.'},
                        {'movie': movies[1], 'body': 'Exciting.'},
                        {'movie': movies[2], 'body': 'Exciting.'},
                        {'movie': movies[2], 'body': 'Exciting.'}]
        for comment in comment_data:
            models.Comment(movie=comment['movie'],
                           body=comment['body']).save()

        now = datetime.now()
        day_ago = str(now - timedelta(days=1))
        now = str(now)
        response = self.client.get('/top/',
                                   {'from_date': day_ago,
                                    'to_date': now})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), [
            {'movie_id': movies[0].id, 'total_comments': 4, 'rank': 1},
            {'movie_id': movies[1].id, 'total_comments': 2, 'rank': 2},
            {'movie_id': movies[2].id, 'total_comments': 2, 'rank': 2},
            {'movie_id': movies[3].id, 'total_comments': 0, 'rank': 3}])
