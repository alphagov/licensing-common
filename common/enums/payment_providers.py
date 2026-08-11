from enum import StrEnum


class PaymentProviders(StrEnum):
    WORLDPAY = "WorldPay"
    ACCESS_PAYSUITE = "Access PaySuite"
    CIVICA = "Civica"
    NORTHGATE = "Northgate"
