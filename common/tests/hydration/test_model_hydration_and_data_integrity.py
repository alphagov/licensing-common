import pytest
from pymongo import MongoClient

from common.models.audit import Audit
from common.models.authority import Authority
from common.models.authority_payment_accounts import AuthorityPaymentAccount
from common.models.department import Department
from common.models.licence import Licence
from common.models.payment import Payment
from common.models.setting import Setting
from common.tests.utils.hydration import verify_model_against_collection
from config import settings


@pytest.mark.skip(reason="Model schema alignment in progress")
@pytest.mark.parametrize(
    "model",
    [
        Audit,
        Authority,
        AuthorityPaymentAccount,
        Department,
        Licence,
        Payment,
        Setting,
    ],
)
def test_django_models_match_document(show_diffs, model):
    with MongoClient(settings.DOCUMENT_DB_CONN) as client:
        db = client["licensify"]
        errors = verify_model_against_collection(db, model, 0, show_diffs)
        assert errors == []
