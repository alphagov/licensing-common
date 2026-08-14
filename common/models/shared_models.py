from django.db import models
from django_mongodb_backend.fields import ObjectIdField
from django_mongodb_backend.models import EmbeddedModel


class PaymentAmount(EmbeddedModel):
    pence = models.IntegerField(default=0)


class SupportingDocumentDefinition(EmbeddedModel):
    name = models.CharField(max_length=255, blank=True, default="")
    description = models.TextField(blank=True)
    is_mandatory = models.BooleanField(db_column="isMandatory", default=False, blank=True)


class PaymentAccount(EmbeddedModel):
    name = models.CharField(db_column="name", max_length=255)
    provider_specific_code_A = models.CharField(db_column="codeA", max_length=255)
    provider_specific_code_B = models.CharField(db_column="codeB", max_length=255)
    provider_specific_code_C = models.CharField(db_column="codeC", max_length=255)
    provider_specific_code_D = models.CharField(db_column="codeD", max_length=255)
    account_id = ObjectIdField(db_column="acc_id", unique=True, blank=True, null=True)
