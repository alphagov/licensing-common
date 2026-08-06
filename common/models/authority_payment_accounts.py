from django.db import models
from django_mongodb_backend.fields import EmbeddedModelArrayField, ObjectIdField
from django_mongodb_backend.models import EmbeddedModel

from common.enums.payment_providers import PaymentProviders


class PaymentAccount(EmbeddedModel):
    name = models.CharField(db_column="name", max_length=255)
    provider_specific_codeA = models.CharField(db_column="codeA", max_length=255)
    provider_specific_codeB = models.CharField(db_column="codeB", max_length=255)
    provider_specific_codeC = models.CharField(db_column="codeC", max_length=255)
    provider_specific_codeD = models.CharField(db_column="codeD", max_length=255)
    account_id = ObjectIdField(db_column="acc_id", unique=True, blank=True, null=True)


class AccessPaySuiteAcceptedCards(EmbeddedModel):
    visa = models.BooleanField(db_column="visa", default=False)
    debit = models.BooleanField(db_column="delt", default=False)
    mastercard = models.BooleanField(db_column="mcrd", default=False)
    maestro = models.BooleanField(db_column="msto", default=False)
    electron = models.BooleanField(db_column="elec", default=False)
    mail_or_telephone_order = models.BooleanField(db_column="moto", default=False)


class AuthorityPaymentAccounts(models.Model):
    authority_url_slug = models.SlugField(db_column="authorityUrlSlug", max_length=255, unique=True)
    payment_provider = models.CharField(
        db_column="paymentProvider",
        max_length=255,
        choices=[(tag.value, tag.name) for tag in PaymentProviders],
        error_messages={"invalid_choice": "Invalid payment provider."},
    )
    accounts = EmbeddedModelArrayField(PaymentAccount, db_column="accounts", default=[], blank=True, null=True)
    merchant_id = models.CharField(db_column="merchantId", max_length=255)
    provider_shared_secret = models.CharField(db_column="providerSharedSecret", max_length=255)
    provider_shared_post_salt = models.CharField(db_column="providerSharedPostSalt", max_length=255, blank=True)
    civica_payment_url = models.CharField(db_column="paymentUrl", max_length=255, blank=True)
    civica_payment_verify_url = models.CharField(db_column="paymentVerifyUrl", max_length=255, blank=True)
    civica_payment_username = models.CharField(db_column="paymentUserName", max_length=255, blank=True)
    civica_payment_password = models.CharField(db_column="paymentPassword", max_length=255, blank=True)
    civica_payment_security_domain = models.CharField(db_column="paymentSecurityDomain", max_length=255, blank=True)
    civica_username_2 = models.CharField(db_column="username2", max_length=255, blank=True)
    civica_password_2 = models.CharField(db_column="password2", max_length=255, blank=True)
    civica_icon_security_use = models.BooleanField(db_column="useIconSecurity", default=False, blank=True)
    mac_secret_key = models.CharField(db_column="macSecretKey", max_length=255, blank=True)
    callback_override_url = models.CharField(db_column="callbackOverride", max_length=255, blank=True)
    send_test_payment = models.BooleanField(db_column="sendTestPayment", default=False, blank=True)
    access_pay_suite_accepted_cards = EmbeddedModel(
        AccessPaySuiteAcceptedCards, db_column="accessPaySuiteAcceptedCards", blank=True
    )
    worldpay_md5_shared_secret = models.CharField(db_column="worldpayMd5SharedSecret", max_length=255, blank=True)

    class Meta:
        db_table = "paymentAccounts"
        managed = False

    def __str__(self):
        return f"{self.authority_url_slug}"
