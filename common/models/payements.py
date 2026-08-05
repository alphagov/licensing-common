import bson
from django.db import models
from django.utils.timezone import now
from django_mongodb_backend.fields import EmbeddedModelField
from django_mongodb_backend.models import EmbeddedModel

from common.enums.payment_providers import PaymentProviders
from common.enums.payment_status import PaymentStatuses
from common.models.shared_models import PaymentAmount


class PaymentStatus(EmbeddedModel):
    status = models.CharField(
        max_length=255,
        choices=[(tag.value, tag.name) for tag in PaymentStatuses],
        error_messages={"invalid_choice": "Payment status %(value)s is not a valid payment status"},
    )


class Payment(models.Model):
    payment_id = models.CharField(
        db_column="id", primary_key=True, default=lambda: str(bson.ObjectId()), editable=False
    )
    application_reference = models.CharField(db_column="applicationReference", max_length=255, default="")
    amount = EmbeddedModelField(PaymentAmount, default=PaymentAmount)
    payment_account_id = models.CharField(db_column="paymentAccountId", max_length=255)
    payment_provider = models.CharField(
        db_column="paymentProvider",
        max_length=255,
        choices=[(tag.value, tag.name) for tag in PaymentProviders],
        error_messages={"invalid_choice": "Payment provider %(value)s is not supported"},
    )
    payment_parameters = models.JSONField(db_column="paymentParameters", default=dict, blank=True)
    payment_status = EmbeddedModelField(PaymentStatus, db_column="status")
    amount_paid_in_pence = models.IntegerField(db_column="paidAmountInPence", blank=True, null=True)
    receipt = models.CharField(db_column="receipt", max_length=255, blank=True)
    transaction_id = models.CharField(db_column="providerTransactionId", max_length=255, blank=True)
    error_details = models.CharField(db_column="errorDetails", max_length=255, blank=True)
    request_url = models.CharField(db_column="requestUrl", max_length=255, default="")
    callback_url = models.CharField(db_column="callbackUrl", max_length=255)
    is_test = models.BooleanField(db_column="isTest", default=False)
    created_at = models.DateTimeField(db_column="createdAt", default=now)
    civica_payment_query_check_count = models.IntegerField(db_column="queryPaymentCheckCount", default=0)

    def __str__(self):
        return self.payment_id
