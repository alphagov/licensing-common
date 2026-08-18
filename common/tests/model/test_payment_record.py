import pytest
from django.core.exceptions import ValidationError

from common.enums.payment_providers import PaymentProviders
from common.models.payment_record import PaymentRecord
from common.models.shared_models import PaymentAccount, PaymentAmount


def test_valid_payment_record():
    payment_record = PaymentRecord(
        application_reference_number="123",
        provider_payment_reference="456",
        payment_amount=PaymentAmount(5000),
        confirmation_record="test confirmation record",
        payment_provider=PaymentProviders.WORLDPAY.value,
        payment_account=PaymentAccount(
            name="test payment account",
            provider_specific_code_A="abc",
            provider_specific_code_B="def",
            provider_specific_code_C="ghi",
            provider_specific_code_D="jkl",
        ),
    )

    payment_record.full_clean()


def test_payment_record_invalid_payment_provider_throws_error():
    expected_error_message = "invalid payment provider is not a supported payment provider"
    with pytest.raises(ValidationError) as e:
        payment_record = PaymentRecord(
            application_reference_number="123",
            provider_payment_reference="456",
            payment_amount=PaymentAmount(5000),
            confirmation_record="test confirmation record",
            payment_provider="invalid payment provider",
            payment_account=PaymentAccount(
                name="test payment account",
                provider_specific_code_A="abc",
                provider_specific_code_B="def",
                provider_specific_code_C="ghi",
                provider_specific_code_D="jkl",
            ),
        )

        payment_record.full_clean()

    assert expected_error_message in e.value.messages
    assert len(e.value.messages) == 1
