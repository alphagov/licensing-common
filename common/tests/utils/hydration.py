import logging
import warnings

from bson import Decimal128, ObjectId
from deepdiff import DeepDiff
from django.db import models
from django_mongodb_backend.models import EmbeddedModel
from pymongo.database import Database

logger = logging.getLogger(__name__)


def verify_model_against_collection(db: Database, model_class: type[models.Model], sample_size=None, show_diffs=False):
    """
    This function compares actual BSON documents from the database with a django model and reports any issues.

    The aim is to see if the model is missing columns, has incompatibility errors,  or not hydrating correctly. It
    compares documents to the model by using pymongo to pull "raw" data and using django to hydrate the equivalent
    model. It then converts both to dictionaries and compares the keys and values directly.

    This is designed to be used against a local database with data that is accurate to reality. Its main goal is to
    increase confidence in initial project release but can help detect database drift and bad data.
    """
    collection_name = model_class._meta.db_table
    # sample checks
    if sample_size == "all" or sample_size is None:
        sample_docs = list(db[collection_name].find())
    else:
        sample_docs = list(db[collection_name].aggregate([{"$sample": {"size": sample_size}}]))
    actual_sample_size = len(sample_docs)
    if actual_sample_size == 0:
        raise ValueError(f"Collection '{collection_name}' has no data")
    elif isinstance(sample_size, int) and actual_sample_size < sample_size:
        warnings.warn(UserWarning(f"{sample_size} asked for, only {actual_sample_size} found."), stacklevel=2)
    elif actual_sample_size < 100:
        warnings.warn(UserWarning("Less than 100 items sampled"), stacklevel=2)
    mismatches = _check_for_mismatches(model_class, sample_docs, show_diffs)
    logger.info(
        "[%s] Verified %s docs in '%s'. Found %s mismatch(es).",
        model_class.__name__,
        len(sample_docs),
        collection_name,
        len(mismatches),
    )
    return mismatches


def _check_for_mismatches(model_class: type[models.Model], sample_docs, show_diffs=False):
    # make sure it returns at least an empty array for mismatches
    mismatches = []
    # create a dictionary that maps database column names to django field names
    db_column_to_field = _map_columns_to_fields(model_class)

    # actual comparisons start here
    for doc in sample_docs:
        # check data exists in both
        doc_id = doc["_id"]
        try:
            django_obj = model_class.objects.get(pk=doc_id)
        except model_class.DoesNotExist:
            mismatches.append(f"[{model_class.__name__}] Doc _id={doc_id} missing in Django ORM.")
            continue
        # check data structure and values match
        for raw_key, raw_val in doc.items():
            # log missing properties at the top level
            structure_mismatch = _check_data_structure(model_class, db_column_to_field, raw_key)
            if structure_mismatch is not None:
                mismatches.append(structure_mismatch)
                continue
            # if the structure is fine, check values
            field_name = db_column_to_field[raw_key]
            mismatches += _check_data_values(model_class, field_name, raw_val, doc_id, django_obj, show_diffs)
    return mismatches


def _map_columns_to_fields(model_class):
    db_column_to_field = {}
    for field in model_class._meta.fields:
        db_column_to_field[field.column] = field.name
    return db_column_to_field


def _check_data_structure(model_class, db_column_to_field, raw_key):
    if raw_key not in db_column_to_field:
        return f"[{model_class.__name__}] Key '{raw_key}' in DB missing from Django model."
    return None


def _check_data_values(model_class, field_name, raw_val, doc_id, django_obj, show_diffs=False):
    value_mismatches = []
    django_val = getattr(django_obj, field_name)

    # to compare we need common ground, normalising the data gets both in a comparable format such as ints, or
    # a dictionary, etc,  and handles known data type quirks
    normalised_bson = _normalise_bson(raw_val)
    normalised_django = _normalise_django(django_val)
    _strip_django_defaults(normalised_bson, normalised_django)

    diffs = DeepDiff(
        normalised_bson,
        normalised_django,
        ignore_numeric_type_changes=True,
        ignore_order=True,
    )

    # at this point we should have 2 identical values, whether it's basic ints or a complex nested dictionary
    # if we don't then the model does not represent the database.
    if diffs:
        for category, items in diffs.items():
            for item in items:
                # instead of root, print the actual field name
                printable_item = str(item).replace("root", field_name, 1)
                value_mismatches.append(
                    f"[{model_class.__name__}] model error. Doc _id: {doc_id}\n"
                    f"  Db value does not match model value. {category} at {printable_item}"
                )

        # use pytest common/tests/hydration/[test_here].py -s --show-diffs for this to log
        # this is to make it almost impossible for any PII to get logged accidentally
        if show_diffs:
            logger.warning(doc_id)
            pretty = diffs.pretty()
            printable_pretty = str(pretty).replace("root", field_name, 1)
            logger.warning("Issue for document %s: \n %s", doc_id, printable_pretty)

    return value_mismatches


def _normalise_common(val, normaliser_fn):
    """
    Handles common cleaning tasks like forcing embedded documents/models to keep recursing through until all the
    primitive data attributes have been normalised and continues
    """
    if val is None:
        return None

    # Recurse so child values are normalised too, also converts tuples and sets to a list
    if isinstance(val, (list, tuple, set)):
        return [normaliser_fn(item) for item in val]

    # If the value is a dictionary then recursion is needed to normalise values but maintain key names
    if isinstance(val, dict):
        return {k: normaliser_fn(v) for k, v in val.items()}

    # Removes whitespace on objectids as one always had a \n and the other didn't
    if isinstance(val, ObjectId):
        return str(val).strip()

    return val


def _normalise_bson(val):
    """
    Ensures bson data convert to predictable/standard data types before common cleaning tasks
    """
    # weird decimal mismatch  make it a normal decimal
    if isinstance(val, Decimal128):
        return val.to_decimal()

    return _normalise_common(val, _normalise_bson)


def _normalise_django(val):
    """
    Handles issues around embedded django models expecting primary keys.
    If it's an embedded model it converts that model to a dictionary skipping primary key.
    Finally hands to the common cleaning tasks
    """
    if val is None:
        return None

    # if it's embedded we skip primary keys because they wont have them in the db
    if isinstance(val, EmbeddedModel):
        normalised_dict = {}
        for field in val._meta.fields:
            if field.primary_key and field.auto_created:
                continue
            field_value = getattr(val, field.name)
            normalised_dict[field.column] = _normalise_django(field_value)
        return normalised_dict

    # regular top level primary key
    if hasattr(val, "_meta"):
        return _normalise_django(val.pk)

    return _normalise_common(val, _normalise_django)


def _strip_django_defaults(bson_val, django_val):
    """
    This removes false positives for data mismatches.
    In the database, even if a field is omitted, the django model will still give it a default value of "" or none.
    """
    if isinstance(bson_val, dict) and isinstance(django_val, dict):
        for key in list(django_val.keys()):
            # this does assume the default value
            if key not in bson_val and django_val[key] in (None, "", [], {}):
                del django_val[key]
            # recurse in case it's an embedded model that needs fixing
            elif key in bson_val:
                _strip_django_defaults(bson_val[key], django_val[key])

    # if it's an array of documents/models we need to recurse until it's removed all false positives
    elif isinstance(bson_val, list) and isinstance(django_val, list):
        for bson_doc, django_model in zip(bson_val, django_val, strict=False):
            _strip_django_defaults(bson_doc, django_model)
