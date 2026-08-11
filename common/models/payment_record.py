import bson
from django.db import models
from django.db.models import DateTimeField
from django_mongodb_backend.fields import EmbeddedModelField, ObjectIdField
from models.shared_models import PaymentAmount


class PaymentRecord(models.Model):
    _id = ObjectIdField(default=bson.ObjectId, auto_created=True, editable=False)
    application_reference_number = models.CharField(
        db_column="applicationRefNo", max_length=255, editable=False, primary_key=True
    )
    payment_amount = EmbeddedModelField(PaymentAmount, db_column="paymentAmount")
    confirmation_time = DateTimeField(db_column="confirmedAt")

    def __str__(self):
        return self.application_reference_number
