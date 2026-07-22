from enum import StrEnum


class TacitConsent(StrEnum):
    PERMITTED = "permitted"
    REQUIRED = "required"
    PROHIBITED = "prohibited"
