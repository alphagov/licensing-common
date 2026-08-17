import bson
from django.core.exceptions import ValidationError
from django.db import models
from django_mongodb_backend.fields import ArrayField, EmbeddedModelArrayField, EmbeddedModelField, ObjectIdField
from django_mongodb_backend.models import EmbeddedModel

from common.enums.countries import Countries, CountryCodes
from common.enums.interaction_id_codes import InteractionIdCodes
from common.enums.tacit_consent import TacitConsent
from common.models.shared_models import PaymentAmount, SupportingDocumentDefinition


class AdministrativeArea(EmbeddedModel):
    code = models.CharField(
        max_length=1,
        choices=[(tag.value, tag.name) for tag in CountryCodes],
        error_messages={"invalid_choice": "Invalid country code."},
    )
    countries = ArrayField(
        models.CharField(
            max_length=255,
            choices=[(tag.value, tag.name) for tag in Countries],
            error_messages={"invalid_choice": "'%(value)s' is not a valid country."},
        ),
        error_messages={"item_invalid": "Invalid entry:"},
    )
    name = models.CharField(max_length=255)

    def clean(self):
        expected_name = ",".join(self.countries)
        name_is_valid = self.name == expected_name
        if not name_is_valid:
            raise ValidationError("Invalid name")


class LicenceForm(EmbeddedModel):
    name = models.CharField(max_length=255, default="defaultName")
    sub_form = models.IntegerField(db_column="subForm", default=0)
    form_ref_number = models.CharField(max_length=255, db_column="formRefNo")
    file_name = models.CharField(max_length=255, default="licenceForm.pdf", db_column="fileName")
    file_size = models.IntegerField(db_column="fileSizeInBytes", default=0)
    form_version = models.IntegerField(db_column="formVersion", default=1)


class LicenceInteraction(EmbeddedModel):
    interaction_id = models.IntegerField(
        db_column="lgilId",
        choices=[(tag.value, tag.name) for tag in InteractionIdCodes],
        default=InteractionIdCodes.APPLY.value,
        error_messages={"invalid_choice": "'%(value)s' is not a valid Interaction Id."},
    )
    interaction_sub_id = models.IntegerField(db_column="lgilSubId", default=0)
    licence_interaction_name = models.CharField(max_length=255, db_column="licenceInteractionName")
    display_title = models.CharField(max_length=255, db_column="displayTitle", blank=True, default="")
    form = EmbeddedModelField(LicenceForm, blank=True, null=True)
    sub_forms = EmbeddedModelArrayField(LicenceForm, db_column="subForms", blank=True, default=list)
    supporting_documents = EmbeddedModelArrayField(
        SupportingDocumentDefinition, db_column="supportingDocuments", default=list, blank=True
    )
    fee = EmbeddedModelField(PaymentAmount, blank=True, default=PaymentAmount())
    fee_calculation_instructions = ArrayField(
        models.TextField(), blank=True, default=[], db_column="feeCalculationInstructions"
    )
    default_declarations = ArrayField(models.TextField(), blank=True, default=list, db_column="defaultDeclarations")
    tacit_consent = models.CharField(
        db_column="tacitConsent",
        max_length=255,
        blank=True,
        choices=[(tag.value, tag.name) for tag in TacitConsent],
        default=TacitConsent.PERMITTED.value,
        error_messages={"invalid_choice": "Invalid consent"},
    )


class Licence(models.Model):
    _id = ObjectIdField(default=bson.ObjectId, editable=False, primary_key=True)
    licence_code = models.CharField(db_column="licenceCode", max_length=255, unique=True)
    name = models.CharField(max_length=255, default="")
    legislation_name = ArrayField(models.CharField(max_length=255), db_column="legislationName")
    url_slug = models.SlugField(max_length=255, db_column="urlSlug")
    local_government_service_list_id = models.IntegerField(
        db_column="lgslId"
    )  # There exists a csv with these noted down that we could validate against..
    administrative_area = EmbeddedModelField(
        AdministrativeArea, db_column="administrativeArea", default=AdministrativeArea()
    )
    is_offered_by_county = models.BooleanField(default=False, db_column="offeredByCounty")
    licence_interactions = EmbeddedModelArrayField(LicenceInteraction, db_column="interactions", default=list)

    class Meta:
        db_table = "elmsLicences"
        managed = False

    def __str__(self):
        return f"{self.licence_code}"

    @property
    def id(self):
        return self.licence_code
