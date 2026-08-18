import bson
from django.db import models
from django.utils import timezone
from django_mongodb_backend.fields import EmbeddedModelArrayField, ObjectIdField
from django_mongodb_backend.models import EmbeddedModel


class EulaAcceptances(EmbeddedModel):
    email = models.EmailField()
    accepted_on = models.DateTimeField(db_column="acceptedOn")


class Eula(models.Model):
    _id = ObjectIdField(default=bson.ObjectId, unique=True, editable=False, primary_key=True)
    version = models.CharField(max_length=255, editable=False, unique=True)
    valid_from = models.DateTimeField(db_column="validFrom", default=timezone.now)
    html_text = models.TextField(db_column="htmlText")
    acceptances = EmbeddedModelArrayField(EulaAcceptances, blank=True, null=True, default=list)

    class Meta:
        db_table = "eula"
        managed = False

    def __str__(self):
        return f"{self.version}"

    @property
    def id(self):
        return self.version
