import bson
from django.db import models
from django.utils.timezone import now
from django_mongodb_backend.fields import EmbeddedModelField, ObjectIdField

from common.enums.payment_providers import PaymentProviders
from common.models.shared_models import PaymentAccount, PaymentAmount


class PaymentRecord(models.Model):
    _id = ObjectIdField(default=bson.ObjectId, editable=False, primary_key=True)
    application_reference_number = models.CharField(
        db_column="applicationRefNo", max_length=255, editable=False, unique=True
    )
    provider_payment_reference = models.CharField(db_column="paymentRef", max_length=255, editable=False)
    payment_amount = EmbeddedModelField(PaymentAmount, db_column="paymentAmount")
    confirmation_time = models.DateTimeField(db_column="confirmedAt", default=now)
    confirmation_record = models.TextField(db_column="confirmationRecord")
    payment_provider = models.CharField(
        db_column="paymentProvider",
        choices=[(tag.value, tag.name) for tag in PaymentProviders],
        error_messages={"invalid_choice": "%(value)s is not a supported payment provider"},
    )
    payment_account = EmbeddedModelField(PaymentAccount, db_column="paymentAccount")
    error_message = models.TextField(db_column="errorMessage", blank=True)
    error_id = models.CharField(db_column="errorId", max_length=255, blank=True)

    class Meta:
        db_table = "paymentRecords"
        managed = False

    def __str__(self):
        return self.application_reference_number

    @property
    def id(self):
        return self.application_reference_number
