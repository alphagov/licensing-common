import bson
from django.db import models
from django.utils.timezone import now
from django_mongodb_backend.fields import EmbeddedModelArrayField, EmbeddedModelField, ObjectIdField
from django_mongodb_backend.models import EmbeddedModel

from common.enums.interaction_id_codes import InteractionIdCodes
from common.enums.virus_check_status import VirusCheckStatus
from common.models.shared_models import PaymentAmount, SupportingDocumentDefinition
from common.models.utils import validate_interaction_id


class SupportingDocument(EmbeddedModel):
    filename = models.CharField(db_column="filename", max_length=255, blank=True)
    stream = models.BinaryField(null=True, blank=True)
    definition = EmbeddedModelField(SupportingDocumentDefinition, db_column="definition")
    _id = ObjectIdField(db_column="_id")
    virus_check_status = models.CharField(
        db_column="virusCheckStatus", max_length=255, default=VirusCheckStatus.CLEAN.value
    )

    @property
    def is_virus_detected_in_file(self) -> bool:
        return self.virus_check_status == VirusCheckStatus.FOUND_VIRUS.value


class Service(EmbeddedModel):
    licence_code = models.CharField(db_column="licenseCode", max_length=255)
    interaction_id = models.IntegerField(
        db_column="lgilId", default=InteractionIdCodes.APPLY.value, validators=[validate_interaction_id]
    )
    interaction_sub_id = models.IntegerField(db_column="lgilSubId")


class ApplicationStatus(EmbeddedModel):
    data_available = models.BooleanField(db_column="isDataAvailable", default=False)
    is_being_processed = models.BooleanField(db_column="isBeingProcessed", default=False)
    processed = models.BooleanField(db_column="successfullyProcessed", default=False)
    collected_by_authority = models.BooleanField(db_column="isCollectedByAuthority", default=False)
    collection_date = models.DateTimeField(db_column="collectionDate", blank=True, null=True)
    is_expired = models.BooleanField(db_column="isExpired", default=False)
    expiry_date = models.DateTimeField(db_column="expiryDate", blank=True, null=True)
    process_attempt_count = models.IntegerField(db_column="processAttemptCount", blank=True, null=True)
    process_start_date = models.DateTimeField(db_column="processStartDate", blank=True, null=True)
    is_downloaded = models.BooleanField(db_column="isDownloaded", default=False)
    download_date = models.DateTimeField(db_column="downloadDate", blank=True, null=True)
    visible_to_authorities = models.BooleanField(db_column="isVisibleToAuthorities", default=False)


class LicenceApplication(models.Model):
    _id = ObjectIdField(db_column="_id", primary_key=True, default=bson.ObjectId, auto_created=True, editable=False)
    applicant_email = models.EmailField(db_column="applicantEmail", default="", max_length=255, blank=True)
    authority = models.CharField(db_column="authority", max_length=255, default="", blank=True)
    licence = models.CharField(db_column="licence", max_length=255, default="", blank=True)
    supporting_documents_online = models.BooleanField(db_column="supportingDocumentsOnline", default=False)
    application_document = EmbeddedModelField(SupportingDocument, db_column="applicationDocument")
    service = EmbeddedModelField(Service, db_column="service")
    application_date = models.DateTimeField(db_column="applicationDate", blank=True, default=now)
    supporting_documents = EmbeddedModelArrayField(
        SupportingDocument, db_column="applicationDocuments", default=[], blank=True
    )
    status = EmbeddedModelField(ApplicationStatus, db_column="status")
    application_data = models.TextField(db_column="applicationData", default="", blank=True)
    application_reference = models.CharField(db_column="applicationRefNo", max_length=255, default="", blank=True)
    authority_application_reference = models.CharField(db_column="authorityAppReference", max_length=255, blank=True)
    expected_processing_date = models.DateTimeField(db_column="expectedProcessingDate", blank=True)
    tacit_consent = models.BooleanField(db_column="tacitConsent", default=False)
    required_payment_amount = EmbeddedModelField(PaymentAmount, db_column="requiredPaymentAmount")
    fee_required = models.BooleanField(db_column="isFeeRequired", default=False)
    variable_fee = models.BooleanField(db_column="isVariableFee", default=False)
    payment_reference_id = models.CharField(db_column="paymentReferenceId", max_length=255, blank=True)
    application_main_form = models.JSONField(db_column="applicationMainForm", default=dict, blank=True)
    collected_by = models.EmailField(db_column="collectedBy", max_length=255, blank=True)
    under_process_by = models.EmailField(db_column="underProcessBy", max_length=255, blank=True)

    class Meta:
        db_table = "applications"
        managed = False

    def __str__(self):
        return f"{self._id}"
