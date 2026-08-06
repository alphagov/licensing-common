from bson import ObjectId

from common.enums.payment_providers import PaymentProviders
from common.models.authority_payment_accounts import (
    AccessPaySuiteAcceptedCards,
    AuthorityPaymentAccounts,
    PaymentAccount,
)


def test_valid_authority_payment_accounts():
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
        civica_payment_url="test",
        civica_payment_verify_url="test",
        civica_payment_username="test",
        civica_payment_password="test",
        civica_payment_security_domain="test",
        civica_username_2="test",
        civica_password_2="test",
        civica_icon_security_use=False,
        mac_secret_key="test",
        callback_override_url="test",
        send_test_payment=False,
        access_pay_suite_accepted_cards=AccessPaySuiteAcceptedCards(),
        worldpay_md5_shared_secret="test",
    )
    authority_payment_accounts.full_clean()
