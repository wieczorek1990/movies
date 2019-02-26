import django_filters

from api import models


class CommentFilter(django_filters.FilterSet):
    class Meta:
        model = models.Comment
        fields = ('movie',)
