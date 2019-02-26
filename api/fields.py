import json

from django.db import models


class JSONField(models.TextField):
    def get_db_prep_value(self, value, connection, prepared=False):
        return json.dumps(value)

    def from_db_value(self, value, expression, connection, context):
        return json.loads(value)
