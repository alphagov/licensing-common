# tests/utils/hydration_engine.py
import warnings

from django.db import models
from pymongo.database import Database


def verify_model_against_collection(
    db: Database, model_class: type[models.Model], collection_name: str, sample_size=100
):
    """This function compares actual BSON documents from the database with a django model.
    The aim is to see if the models are missing columns or not hydrating correctly by comparing raw data to the model.
    The usefulness of the test depends entirely on having access to a db with data to sample.
    """

    sample_docs = list(db[collection_name].aggregate([{"$sample": {"size": sample_size}}]))
    actual_sample_size = len(sample_docs)

    assert actual_sample_size > 0, f"Collection '{collection_name}' has no data"
    if actual_sample_size < sample_size:
        warnings.warn(UserWarning(f"{sample_size} asked for, only {actual_sample_size} found."), stacklevel=2)

    db_column_to_field = {}
    for field in model_class._meta.fields:
        db_column_to_field[field.column] = field.name
    mismatches = []
    for doc in sample_docs:
        doc_id = doc["_id"]
        try:
            django_obj = model_class.objects.get(pk=str(doc_id))
        except model_class.DoesNotExist:
            mismatches.append(f"[{model_class.__name__}] Doc _id={doc_id} missing in Django ORM.")
            continue

        for raw_key, raw_val in doc.items():
            if raw_key not in db_column_to_field.keys():
                mismatches.append(f"[{model_class.__name__}] Key '{raw_key}' in DB missing from Django model.")
                continue

            field_name = db_column_to_field[raw_key]
            django_val = getattr(django_obj, field_name)

            if normalize_bson(raw_key, raw_val) != normalize_django(django_val):
                mismatches.append(
                    f"[{model_class.__name__}] model error. Doc _id: {doc_id} | Field: '{field_name}'\n"
                    f"  Db value does not match model value."
                )
    return mismatches


def normalize_bson(key, val):
    # a stray new line was getting in for ids
    if key == "_id" and isinstance(val, str):
        return val.strip()
    return val


def normalize_django(val):
    pk_or_val = val.pk if hasattr(val, "pk") else val

    return pk_or_val
