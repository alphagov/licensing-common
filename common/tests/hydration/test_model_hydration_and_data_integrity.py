import pytest
from pymongo import MongoClient

from common.models.audit import Audit

# from common.models.authorities import Authority
# from common.models.authority_payment_accounts import AuthorityPaymentAccounts
# from common.models.department import Department
# from common.models.licences import Licence
# from common.models.payments import Payment
# from common.models.setting import Setting
from common.tests.utils.hydration import verify_model_against_collection
from config import settings


# @pytest.mark.skip(reason="Model schema alignment in progress")
@pytest.mark.parametrize(
    "model",
    [
        Audit
        # Authority, AuthorityPaymentAccounts, Department, Licence, Payment, Setting,
    ],
)
def test_django_models_match_document(show_diffs, model):
    with MongoClient(settings.DOCUMENT_DB_CONN) as client:
        db = client["licensify"]
        errors = verify_model_against_collection(db, model, 0, show_diffs)
        assert errors == []
