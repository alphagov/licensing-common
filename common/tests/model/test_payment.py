import pytest
from django.core.exceptions import ValidationError

from common.enums.payment_status import PaymentStatuses
from common.models.payments import Payment, PaymentStatus


def test_valid_payment():
    payment = Payment(
        payment_account_id="test",
        payment_provider="WorldPay",
        application_reference="test",
        payment_status=PaymentStatus(status=PaymentStatuses.COMPLETED),
        callback_url="https://example.com",
        request_url="https://example.com",
    )

    payment.full_clean()


def test_payment_invalid_payment_status_throws_error():
    expected_error_message = "Payment status invalid is not a valid payment status"
    with pytest.raises(ValidationError) as e:
        payment = Payment(
            payment_account_id="test",
            payment_provider="WorldPay",
            application_reference="test",
            payment_status=PaymentStatus(status="invalid"),
            callback_url="https://example.com",
            request_url="https://example.com",
        )
        payment.full_clean()

    assert e.value.messages == [expected_error_message]


def test_payment_invalid_payment_payment_provider_throws_error():
    expected_error_message = "Payment provider invalid is not supported"
    with pytest.raises(ValidationError) as e:
        payment = Payment(
            payment_account_id="test",
            application_reference="test",
            payment_provider="invalid",
            payment_status=PaymentStatus(status=PaymentStatuses.COMPLETED),
            callback_url="https://example.com",
            request_url="https://example.com",
        )
        payment.full_clean()

    assert e.value.messages == [expected_error_message]
