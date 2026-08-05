from enum import StrEnum


class VirusCheckStatus(StrEnum):
    CLEAN = "Clean"
    FOUND_VIRUS = "FoundVirus"
