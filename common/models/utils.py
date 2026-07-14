from common.enums.countries import Countries, CountryCodes
from django.core.exceptions import ValidationError

from common.enums.tacit_consent import TacitConsent
from common.enums.interaction_id_codes import InteractionIdCodes


def validate_countries(countries: list):
    for country in countries:
        if country not in Countries:
            raise ValidationError("Invalid country")


def validate_country_code(country_code: str):
    if country_code not in CountryCodes:
        raise ValidationError("Invalid country code")


def validate_consent(consent: str):
    if consent not in TacitConsent:
        raise ValidationError("Invalid consent")

def validate_interaction_id(interaction_id: int):
    if interaction_id not in InteractionIdCodes:
        raise ValidationError("Invalid interaction id")