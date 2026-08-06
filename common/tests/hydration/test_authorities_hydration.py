from pymongo import MongoClient

from common.models.authorities import Authority
from common.tests.utils.hydration import verify_model_against_collection
from config import settings


def test_django_models_match_document():
    with MongoClient(settings.DOCUMENT_DB_CONN) as client:
        db = client["licensify"]
        errors = verify_model_against_collection(db, Authority, 1000)
        assert errors == []
