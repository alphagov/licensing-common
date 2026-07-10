from django.core.exceptions import ValidationError
from django.db import models
from django_mongodb_backend.fields import ArrayField
from django_mongodb_backend.models import EmbeddedModel
from apply_for_a_licence.models.utils import validate_countries


class AdministrativeArea(EmbeddedModel):

    def validate_name(self, name: str):
        expected_name = ','.join(set(self.countries))

        if name != expected_name:
            raise ValidationError("Invalid name")

    code = models.CharField()
    countries = ArrayField(models.CharField(), validators=[validate_countries])
    name = models.CharField(max_length=255)

    def clean(self):
        expected_name = ','.join(self.countries)
        name_is_valid = self.name == expected_name
        if not name_is_valid:
            raise ValidationError("Invalid name")









