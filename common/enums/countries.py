from enum import StrEnum

class Countries(StrEnum):
    ENGLAND = "England"
    NORTHERN_IRELAND = "NI"
    WALES = "Wales"
    SCOTLAND = "Scotland"

class CountryCodes(StrEnum):
    ENGLAND = "1"
    WALES = "2"
    SCOTLAND = "3"
    NI = "4"
    ENGLAND_AND_WALES = "5"
    ENGLAND_SCOTLAND_AND_WALES = "6"
    ALL = "7"