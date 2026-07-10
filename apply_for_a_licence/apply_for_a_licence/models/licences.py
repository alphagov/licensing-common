from django.core.exceptions import ValidationError
from django.db import models
from django_mongodb_backend.fields import ArrayField
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
    pence = models.IntegerField()


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
















