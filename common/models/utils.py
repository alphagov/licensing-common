from django.core.exceptions import ValidationError

from common.enums.countries import Countries
from common.enums.snac_codes import SnacCodes


def validate_countries(countries: list):
    for country in countries:
        if country not in Countries:
            raise ValidationError("Invalid country")


def validate_snac_codes(snac_codes: list):
    if not set(snac_codes).issubset(set(SnacCodes.list())):
        raise ValidationError("Snac codes not valid")
