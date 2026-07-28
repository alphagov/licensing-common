from django.db import models
from django_mongodb_backend.models import EmbeddedModel


class PaymentAmount(EmbeddedModel):
    pence = models.IntegerField(default=0)

class SupportingDocumentDefinition(EmbeddedModel):
    name = models.CharField(max_length=255, blank=True, default="")
    description = models.TextField(blank=True)
    is_mandatory = models.BooleanField(db_column="isMandatory", default=False, blank=True)