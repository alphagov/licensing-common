import bson
from django.db import models
from django_mongodb_backend.fields import ObjectIdField


class Settings(models.Model):
    _id = ObjectIdField(default=bson.ObjectId, unique=True, editable=False, primary_key=True)
    key = models.CharField(max_length=255, unique=True)
    value = models.CharField(max_length=255, unique=True)

    class Meta:
        db_table = "settings"
        managed = False

    def __str__(self):
        return f"{self.key}"

    @property
    def id(self):
        return self.key
