from django.core.exceptions import ValidationError

from common.enums.snac_codes import SnacCodes


def validate_snac_codes(snac_codes: list):
    if not set(snac_codes).issubset(set(SnacCodes.list())):
        raise ValidationError("Snac codes not valid")
