from apply_for_a_licence.enums.countries import Countries
from django.core.exceptions import ValidationError


def validate_countries(countries: list):
    for country in countries:
        if country not in Countries:
            raise ValidationError("Invalid country")