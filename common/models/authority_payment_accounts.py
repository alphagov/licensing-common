from django.db import models
from django_mongodb_backend.fields import ObjectIdField
from django_mongodb_backend.models import EmbeddedModel


class PaymentAccount(EmbeddedModel):
    name = models.CharField(db_column="name", max_length=255)
    provider_specific_codeA = models.CharField(db_column="codeA", max_length=255)
    provider_specific_codeB = models.CharField(db_column="codeB", max_length=255)
    provider_specific_codeC = models.CharField(db_column="codeC", max_length=255)
    provider_specific_codeD = models.CharField(db_column="codeD", max_length=255)
    account_id = ObjectIdField(db_column="acc_id", unique=True, blank=True, null=True)
