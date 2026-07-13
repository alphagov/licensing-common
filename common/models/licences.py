import bson
from django.core.exceptions import ValidationError
from django.db import models
from django_mongodb_backend.fields import ArrayField, EmbeddedModelField, EmbeddedModelArrayField, ObjectIdField
from django_mongodb_backend.models import EmbeddedModel
from common.models.utils import validate_countries
from common.enums.tacit_consent import TacitConsent
from common.enums.interaction_id_codes import InteractionIdCodes
from models.utils import validate_country_code


class AdministrativeArea(EmbeddedModel):
    code = models.CharField(max_length=1, validators=[validate_country_code])
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
    sub_form = models.IntegerField(db_column="subForm", default=0)
    form_ref_number = models.CharField(max_length=255, db_column="formRefNo")
    file_name = models.CharField(max_length=255, default="licenceForm.pdf", db_column="fileName")
    file_size = models.IntegerField(db_column="fileSizeInBytes", default=0)
    form_version = models.IntegerField(db_column="formVersion", default=1)


class SupportingDocumentDefinition(EmbeddedModel):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    is_mandatory = models.BooleanField(db_column="isMandatory", default=False)


class LicenceInteraction(EmbeddedModel):
    interaction_id = models.IntegerField(db_column="lgilId", default=InteractionIdCodes.APPLY.value)
    interaction_sub_id = models.IntegerField(db_column="lgilSubId", default=0)
    licence_interaction_name = models.CharField(max_length=255, db_column="licenceInteractionName") #generated field from interaction id?
    display_title = models.CharField(max_length=255, db_column="displayTitle", blank=True, default="")
    form = EmbeddedModelField(LicenceForm, blank=True)
    sub_forms = EmbeddedModelArrayField(LicenceForm, db_column="subForms", blank=True, default=[])
    supporting_documents = EmbeddedModelArrayField(SupportingDocumentDefinition, db_column="supportingDocuments", default=[])
    fee = EmbeddedModelField(PaymentAmount, blank=True, default=PaymentAmount())
    fee_calculation_instructions = ArrayField(models.TextField(), blank=True, default=[], db_column="feeCalculationInstructions")
    default_declarations = ArrayField(models.TextField(), blank=True, default=[], db_column="defaultDeclarations")
    tacit_consent = models.CharField(db_column="tacitConsent", max_length=255, blank=True, default=TacitConsent.PERMITTED.value)


class Licence(models.Model):
    _id = ObjectIdField(default=bson.ObjectId, auto_created=True, editable=False, primary_key=True)
    licence_code = models.CharField(db_column="licenceCode", max_length=255)
    name = models.CharField(max_length=255, default="")
    legislation_name = ArrayField(models.CharField(max_length=255), blank=True, default=[], db_column="legislationName")
    url_slug = models.SlugField(max_length=255, default="", db_column="urlSlug")
    local_government_service_list_id = models.IntegerField(default=0, db_column="lgslId")
    administrative_area = EmbeddedModelField(AdministrativeArea, db_column="administrativeArea", default=AdministrativeArea())
    is_offered_by_county = models.BooleanField(default=False, db_column="offeredByCounty")
    licence_interactions = EmbeddedModelArrayField(LicenceInteraction, db_column="interactions", default=[])
#   email templates appears in the model audit, struggling to find any mention of these from the models in the scala code,
    #   seems to be pulled through from the config

    class Meta:
        db_table = "elmsLicences"
        managed = False













