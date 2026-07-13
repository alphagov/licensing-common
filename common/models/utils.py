from common.enums.countries import Countries, CountryCodes
from django.core.exceptions import ValidationError


def validate_countries(countries: list):
    for country in countries:
        if country not in Countries:
            raise ValidationError("Invalid country")


def validate_country_code(country_code: str):
    if country_code not in CountryCodes:
        raise ValidationError("Invalid country code")