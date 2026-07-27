from django.db import models
from django_mongodb_backend.fields import EmbeddedModelField, ObjectIdField
from django_mongodb_backend.models import EmbeddedModel

from common.models.licences import SupportingDocumentDefinition


class SupportingDocument(EmbeddedModel):
    filename = models.CharField(db_column="filename", max_length=255, blank=True)
    definition = EmbeddedModelField(SupportingDocumentDefinition, db_column="definition")
    _id = ObjectIdField(db_column="_id")
    virus_check_status = models.CharField(db_column="virusCheckStatus", max_length=255)#"Clean" or "FoundVirus"
    # stream = runtime only field

class SupportingDocumentDefinition(EmbeddedModel):
    name = models.CharField(db_column="name", max_length=255)
    description = models.CharField(db_column="description", max_length=255, default="", blank=True)
    required = models.BooleanField(db_column="isMandatory", default=False)

