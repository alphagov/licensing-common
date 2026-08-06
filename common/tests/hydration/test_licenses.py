from pymongo import MongoClient

from common.models.licences import Licence
from common.tests.utils.hydration import verify_model_against_collection
from config import settings


def test_django_models_match_document(show_diffs):
    with MongoClient(settings.DOCUMENT_DB_CONN) as client:
        db = client["licensify"]
        errors = verify_model_against_collection(db, Licence, 100, show_diffs)
        assert errors == []
