import bson
from django.db import models
from django.utils import timezone
from django_mongodb_backend.fields import ArrayField, EmbeddedModelArrayField, EmbeddedModelField, ObjectIdField
from django_mongodb_backend.models import EmbeddedModel

from common.enums.interaction_id_codes import InteractionIdCodes
from common.models.shared_models import PaymentAmount, SupportingDocumentDefinition


class Customisation(EmbeddedModel):
    is_postal_allowed = models.BooleanField(db_column="isAllowedPosting")
    number_of_days_to_process = models.IntegerField(db_column="processingDays")
    is_processing_days_working_days = models.BooleanField(db_column="processingWorkingDays")
    has_tacit_consent = models.BooleanField(db_column="tacitConsent")
    created_at = models.DateTimeField(db_column="created", default=timezone.now)
    is_fee_required = models.BooleanField(db_column="isFeeRequired")
    fixed_fee_amount = EmbeddedModelField(PaymentAmount, db_column="fixedFeeAmount", blank=True, null=True)
    fee_calculation_instructions = ArrayField(
        models.TextField(), db_column="feeCalculationInstructions", blank=True, null=True, default=list
    )
    payment_account = models.CharField(db_column="paymentAccount", max_length=255, blank=True)
    supporting_document_definitions = EmbeddedModelArrayField(
        SupportingDocumentDefinition, db_column="supportingDocuments", default=list, blank=True
    )
    legislation_name = models.CharField(db_column="legislation", max_length=255)
    introduction_text = models.TextField(db_column="introductionText")
    declarations = ArrayField(models.TextField(), db_column="declarations", default=list)
    guidance_url = models.CharField(db_column="guidanceUrl", max_length=255, blank=True)
    information_url = models.CharField(db_column="informationUrl", max_length=255, blank=True)
    privacy_notice_url = models.CharField(db_column="privacyNoticeUrl", max_length=255, blank=True)
    department = ObjectIdField()
    purchase_code = models.CharField(db_column="purchaseCode", max_length=255, blank=True)
    published_at = models.DateTimeField(db_column="publishedDate", blank=True, null=True)
    suspended_at = models.DateTimeField(db_column="suspendedDate", blank=True, null=True)
    user_id = models.CharField(db_column="userId", max_length=255, blank=True)
    customisation_id = ObjectIdField(db_column="c_id", blank=True, null=True)


class InteractionCustomisation(models.Model):
    _id = ObjectIdField(default=bson.ObjectId, unique=True, editable=False, primary_key=True)
    authority_slug_url = models.CharField(db_column="authoritySlugUrl", max_length=255)
    licence_code = models.CharField(db_column="licenseCode", max_length=255)
    interaction_id = models.IntegerField(
        db_column="lgilId",
        choices=[(tag.value, tag.name) for tag in InteractionIdCodes],
        default=InteractionIdCodes.APPLY.value,
        error_messages={"invalid_choice": "'%(value)s' is not a valid Interaction Id."},
    )
    interaction_sub_id = models.IntegerField(db_column="lgilSubId", default=999)
    pending_customisation = EmbeddedModelField(Customisation, db_column="pendingCustomisation", blank=True, null=True)
    published_customisation = EmbeddedModelField(
        Customisation, db_column="publishedCustomisation", blank=True, null=True
    )

    class Meta:
        db_table = "customisations"
        managed = False

    def __str__(self):
        return str(self._id)
