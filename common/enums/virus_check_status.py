from enum import StrEnum


# TODO this might not be needed any more,
#  need to have a think about whether we scan before uploading or keep the same mechanism..
class VirusCheckStatus(StrEnum):
    CLEAN = "Clean"
    FOUND_VIRUS = "FoundVirus"
