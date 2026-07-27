from django.db import models
from django_mongodb_backend.fields import EmbeddedModelField, ObjectIdField
from django_mongodb_backend.models import EmbeddedModel

from common.models.licences import SupportingDocumentDefinition


class SupportingDocument(EmbeddedModel):
    filename = models.CharField(blank=True, max_length=255, db_column="filename")
    definition = EmbeddedModelField(SupportingDocumentDefinition, db_column="definition")
    _id = ObjectIdField(db_column="_id")
    virus_check_status = models.CharField(max_length=255, db_column="virusCheckStatus")#"Clean" or "FoundVirus"
    # stream = runtime only field

