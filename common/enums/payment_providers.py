from enum import StrEnum


class PaymentProviders(StrEnum):
    CIVICA = "Civica"
    NORTHGATE = "Northgate"
    WORLDPAY = "WorldPay"
    ACCESS_PAY_SUITE = "Access PaySuite"
