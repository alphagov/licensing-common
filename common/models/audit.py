import bson
from django.db import models
from django.utils import timezone
from django_mongodb_backend.fields import ArrayField, ObjectIdField


class Audit(models.Model):
    _id = ObjectIdField(default=bson.ObjectId, unique=True, editable=False, primary_key=True)
    timestamp = models.DateTimeField(default=timezone.now)
    audit_type = models.CharField(db_column="auditType", max_length=255)
    unique_tag_ids = ArrayField(
        models.CharField(max_length=255), db_column="uniqueTagIds", blank=True, null=True, default=list
    )
    tags = models.JSONField(default=dict)
    details = models.JSONField(db_column="detail", default=dict)
    hostname = models.CharField(max_length=255)

    class Meta:
        db_table = "audit"
        managed = False

    # this explicitly mimics the old system as it's unclear what (if anything) relies on this being a specific format
    def __str__(self):
        type_str = "Type: " + self.audit_type
        tags_str = "Tags: " + ", ".join(f"{k}: {v}" for k, v in self.tags.items())
        details_str = "Detail: " + ", ".join(f"{k}: {v}" for k, v in self.details.items())
        hostname_str = "Hostname: " + self.hostname
        timestamp_str = "Timestamp: " + self.timestamp.strftime("%Y-%m-%d %H:%M:%S")  # "2026-08-26 13:52:00"
        return " | ".join(["[AuditEvent", type_str, tags_str, details_str, hostname_str, timestamp_str + "]"])
