from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import ExpressionWrapper, CharField
from django_mongodb_backend.fields import ArrayField
from django_mongodb_backend.models import EmbeddedModel

from apply_for_a_licence.enums.countries import Countries

def validate_countries(countries: list):
    for country in countries:
        if country not in Countries:
            raise ValidationError("Invalid country")




class AdministrativeArea(EmbeddedModel):
    code = models.CharField()
    countries = ArrayField(models.CharField(), validators=[validate_countries])
    name = models.GeneratedField(expression=ExpressionWrapper(",".join("countries"),
                                                              output_field=CharField()),
                                 output_field=CharField(),
                                 db_persist=True)


    def validate_name(self, name: str):
        expected_name = ','.join(set(self.countries))

        if name != expected_name:
            raise ValidationError("Invalid name")




