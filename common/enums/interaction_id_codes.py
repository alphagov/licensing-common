from enum import IntEnum

# this may need to become a multi value enum, ID code, and string representation?
# or second enum, id to string value, scala codebase has a function on the model against a map to capitalise a string and remove "-"
class InteractionIdCodes(IntEnum):
    APPLY = 0
    PAY_FOR = 4
    INFORMATION = 8
    REGULATION = 9
    CHANGE = 11
    RENEW = 14
    APPLY_FOR_EXEMPTION = 30
    TELL_US_ONCE = 31
    NOTIFY_OF_INCIDENT_OR_INSTANCES = 32
    UNKNOWN = 999