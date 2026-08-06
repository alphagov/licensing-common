import pytest
from bson import ObjectId
from django.core.exceptions import ValidationError

from common.enums.payment_providers import PaymentProviders
from common.models.authority_payment_accounts import (
    AccessPaySuiteAcceptedCards,
    AuthorityPaymentAccounts,
    PaymentAccount,
)


def test_valid_authority_payment_accounts_with_civica():
    authority_payment_accounts = AuthorityPaymentAccounts(
        authority_url_slug="test",
        payment_provider=PaymentProviders.CIVICA,
        accounts=[
            PaymentAccount(
                name="test",
                provider_specific_code_A="test",
                provider_specific_code_B="test",
                provider_specific_code_C="test",
                provider_specific_code_D="test",
                account_id=ObjectId(),
            )
        ],
        merchant_id="test",
        provider_shared_secret="test",
        provider_shared_post_salt="test",
        civica_payment_form_url="test",
        civica_payment_verify_url="test",
        use_icon_security=False,
        iron_security_auth_username="test",
        iron_security_auth_password="test",
        payment_security_domain="test",
        basic_auth_username="test",
        basic_auth_password="test",
        mac_secret_key="test",
        callback_override_url="test",
        send_test_payment=False,
        access_pay_suite_accepted_cards=AccessPaySuiteAcceptedCards(),
        worldpay_md5_shared_secret="test",
    )
    authority_payment_accounts.full_clean()


def test_valid_authority_payment_accounts_without_civica():
    authority_payment_accounts = AuthorityPaymentAccounts(
        authority_url_slug="test",
        payment_provider=PaymentProviders.NORTHGATE,
        accounts=[
            PaymentAccount(
                name="test",
                provider_specific_code_A="test",
                provider_specific_code_B="test",
                provider_specific_code_C="test",
                provider_specific_code_D="test",
                account_id=ObjectId(),
            )
        ],
        merchant_id="test",
        provider_shared_secret="test",
        provider_shared_post_salt="test",
        mac_secret_key="test",
        callback_override_url="test",
        send_test_payment=False,
        access_pay_suite_accepted_cards=AccessPaySuiteAcceptedCards(),
        worldpay_md5_shared_secret="test",
    )
    authority_payment_accounts.full_clean()


def test_invalid_payment_provider():
    expected_error_message = "'test' is not a valid payment provider."
    with pytest.raises(ValidationError) as e:
        invalid_payment_provider = AuthorityPaymentAccounts(payment_provider="test")
        invalid_payment_provider.full_clean()

    assert expected_error_message in e.value.message_dict["payment_provider"]


def test_authority_payment_accounts_id():
    authority_payment_accounts = AuthorityPaymentAccounts(
        authority_url_slug="test",
        payment_provider=PaymentProviders.NORTHGATE,
        accounts=[],
        merchant_id="test",
        provider_shared_secret="test",
        provider_shared_post_salt="test",
        mac_secret_key="test",
        callback_override_url="test",
        send_test_payment=False,
        access_pay_suite_accepted_cards=AccessPaySuiteAcceptedCards(),
        worldpay_md5_shared_secret="test",
    )
    authority_payment_accounts.full_clean()

    assert authority_payment_accounts.id == "test"
