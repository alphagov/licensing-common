from enum import StrEnum


class PaymentStatuses(StrEnum):
    CREATED = "created"
    SENT_TO_PROVIDER = "sentToProvider"
    COMPLETED = "completed"
    TIMED_OUT = "cancelledExpired"
    BACK_PRESSED = "backPressed"
    FAILED = "failedNotPaid"
    UNKNOWN = "unknown"
    FAILED_UNKNOWN = "failedUnknownState"
    MISMATCHED = "mismatched"
    CIVICA_RETURNED = "returnedFromPaymentProvider"
    CANCELLED = "cancelled"
    UNKNOWN_EXPIRED = "unknownExpired"
