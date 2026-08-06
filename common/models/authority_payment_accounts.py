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


class AccessPaySuiteAcceptedCards(EmbeddedModel):
    visa = models.BooleanField(db_column="visa", default=False)
    debit = models.BooleanField(db_column="delt", default=False)
    mastercard = models.BooleanField(db_column="mcrd", default=False)
    maestro = models.BooleanField(db_column="msto", default=False)
    electron = models.BooleanField(db_column="elec", default=False)
    mail_or_telephone_order = models.BooleanField(db_column="moto", default=False)
