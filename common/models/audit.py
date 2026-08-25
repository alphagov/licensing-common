import bson
from django.db import models
from django.utils import timezone
from django_mongodb_backend.fields import ArrayField, ObjectIdField


class Audit(models.Model):
    _id = ObjectIdField(default=bson.ObjectId, unique=True, editable=False, primary_key=True)
    timestamp = models.DateTimeField(default=timezone.now)
    audit_type = models.CharField(db_column="auditType", max_length=255)
    unique_tag_ids = ArrayField(models.CharField(max_length=255), db_column="uniqueTagIds", blank=True)
    tags = models.JSONField(default=dict)
    details = models.JSONField(db_column="detail", default=dict)
    hostname = models.CharField(max_length=255)

    class Meta:
        db_table = "audit"
        managed = False

    def __str__(self):
        return f"{self.version}"

    @property
    def id(self):
        return self.version
