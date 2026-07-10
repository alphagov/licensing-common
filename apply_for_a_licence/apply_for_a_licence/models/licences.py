import bson
from django.core.exceptions import ValidationError
from django.db import models
from django_mongodb_backend.fields import ArrayField, EmbeddedModelField, EmbeddedModelArrayField, ObjectIdField
from django_mongodb_backend.models import EmbeddedModel
from apply_for_a_licence.models.utils import validate_countries


class AdministrativeArea(EmbeddedModel):
    code = models.CharField()
    countries = ArrayField(models.CharField(), validators=[validate_countries])
    name = models.CharField(max_length=255)

    def clean(self):
        expected_name = ','.join(self.countries)
        name_is_valid = self.name == expected_name
        if not name_is_valid:
            raise ValidationError("Invalid name")


class PaymentAmount(EmbeddedModel):
    pence = models.IntegerField(default=0)


class LicenceForm(EmbeddedModel):
    name = models.CharField(max_length=255, default="defaultName")
    sub_form = models.IntegerField(db_column="subForm")
    form_ref_number = models.CharField(max_length=255, db_column="formRefNo")
    file_name = models.CharField(max_length=255, default="licenceForm.pdf", db_column="fileName")
    file_size = models.IntegerField(db_column="fileSizeInBytes")
    form_version = models.IntegerField(db_column="formVersion")


class SupportingDocumentDefinition():
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    is_mandatory = models.BooleanField(db_column="isMandatory")


class LicenceInteraction(EmbeddedModel):
    interaction_id = models.IntegerField(db_column="lgilId")
    interaction_sub_id = models.IntegerField(db_column="lgilSubId")
    licence_interaction_name = models.CharField(max_length=255, db_column="licenceInteractionName")
    display_title = models.CharField(max_length=255, db_column="displayTitle", blank=True)
    form = EmbeddedModelField(LicenceForm)
    sub_forms = EmbeddedModelArrayField(LicenceForm, db_column="subForms", blank=True, default=[])
    supporting_documents = EmbeddedModelArrayField(SupportingDocumentDefinition, db_column="supportingDocuments")
    fee = EmbeddedModelField(PaymentAmount, blank=True, default=PaymentAmount())
    fee_calculation_instructions = ArrayField(models.CharField(max_length=255), blank=True, default=[], db_column="feeCalculationInstructions")
    default_declarations = ArrayField(models.CharField(max_length=255), blank=True, default=[], db_column="defaultDeclarations")
    tacit_consent = models.CharField(db_column="tactConsent", max_length=255, blank=True)


class Licence(models.Model):
    _id = ObjectIdField(default=bson.ObjectId, auto_created=True, editable=False, primary_key=True)
    licence_code = models.CharField(db_column="licenceCode", max_length=255)
    name = models.CharField(max_length=255, default="")
    legislation_name = ArrayField(models.CharField(max_length=255), blank=True, default=[])
    url_slug = models.SlugField(max_length=255, default="")
    local_government_service_list_id = models.IntegerField(default=0, db_column="lgslId")
    administrative_area = EmbeddedModelField(AdministrativeArea, db_column="administrativeArea", default={})
    is_offered_by_county = models.BooleanField(default=False, db_column="offeredByCounty")
    licence_interactions = EmbeddedModelArrayField(LicenceInteraction, db_column="interactions", default=[])
#   email templates appears in the model audit, struggling to find any mention of these from the model, seems to be pulled through from the config














