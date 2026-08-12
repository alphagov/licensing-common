import pytest
from pymongo import MongoClient

from common.models.authority_payment_accounts import AuthorityPaymentAccounts
from common.tests.utils.hydration import verify_model_against_collection
from config import settings


@pytest.mark.skip(reason="Model schema alignment in progress")
def test_django_models_match_document(show_diffs):
    with MongoClient(settings.DOCUMENT_DB_CONN) as client:
        db = client["licensify"]
        errors = verify_model_against_collection(db, AuthorityPaymentAccounts, "all", show_diffs)
        assert errors == []
