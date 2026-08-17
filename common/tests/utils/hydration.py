import logging
import warnings

from bson import Decimal128, ObjectId
from deepdiff import DeepDiff
from django.core.exceptions import ValidationError
from django.db import models
from django_mongodb_backend.models import EmbeddedModel
from pymongo.database import Database

logger = logging.getLogger(__name__)


def verify_model_against_collection(db: Database, model_class: type[models.Model], sample_size=None, show_diffs=False):
    """
    This function compares actual documents from the database (via pymongo)  with a django model and reports any issues.

    The aim is to see if the model is missing attributes, has incompatibility errors,  or not hydrating correctly. It
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
        warnings.warn(
            f"{sample_size} asked for, only {actual_sample_size} found.",
            category=UserWarning,
            stacklevel=2,
        )
    elif actual_sample_size < 100:
        warnings.warn(
            "Less than 100 items sampled",
            category=UserWarning,
            stacklevel=2,
        )
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
    # create a dictionary that maps database attribute names to django field names
    db_attribute_to_field = _get_explicitly_declared_attributes(model_class)

    # actual comparisons start here
    for doc in sample_docs:
        real_primary_key_col = model_class._meta.pk.column

        # check data exists in both
        doc_id = doc[real_primary_key_col]
        try:
            django_obj = model_class.objects.get(pk=doc_id)
        except model_class.DoesNotExist:
            mismatches.append(f"[{model_class.__name__}] Doc _id={doc_id} missing in Django ORM.")
            continue

        # forces the validation rules to run, so enum properties and custom rules that normally only occur on form fills
        # tests the model matches reality (or the quality of the data)
        validation_errors = _get_clean_errors(django_obj, model_class)
        for err in validation_errors:
            mismatches.append(f"[{model_class.__name__}] Doc _id={doc_id}: {err}")

        # check data structure and values match
        for raw_key, raw_val in doc.items():
            # if there's an _id BUT it isn't the primary key of the model AND we haven't mapped it, let's assume it's
            # an intentional choice to leave it out
            if raw_key == "_id" and real_primary_key_col != "_id" and "_id" not in db_attribute_to_field:
                continue
            # log missing properties at the top level
            structure_mismatch = _check_data_structure(model_class, db_attribute_to_field, raw_key)
            if structure_mismatch is not None:
                mismatches.append(structure_mismatch)
                continue
            # if the structure is fine, check values
            field_name = db_attribute_to_field[raw_key]
            mismatches += _check_data_values(model_class, field_name, raw_val, doc_id, django_obj, show_diffs)
    return mismatches


def _get_clean_errors(django_obj, model_class):
    clean_errors = []

    try:
        django_obj.full_clean(validate_unique=False)
    except ValidationError as e:
        msg = e.message_dict if hasattr(e, "message_dict") else e.messages
        clean_errors.append(f"Parent validation error: {msg}")

    return clean_errors


def _is_django_implicit_auto_pk(field: models.Field) -> bool:
    """
    Returns True ONLY if this field is Django's default auto-injected primary key.
    """
    return field.auto_created and field.name == "id"


def _get_explicitly_declared_attributes(model_class):
    # basically we're trying to avoid useless django ids
    return {field.column: field.name for field in model_class._meta.fields if not _is_django_implicit_auto_pk(field)}


def _check_data_structure(model_class, db_attribute_to_field, raw_key):
    if raw_key not in db_attribute_to_field:
        return f"[{model_class.__name__}] Key '{raw_key}' in DB missing from Django model."
    return None


def _check_data_values(model_class, field_name, raw_val, doc_id, django_obj, show_diffs=False):
    value_mismatches = []
    django_val = getattr(django_obj, field_name)

    # to compare we need common ground, normalising the data gets both in a comparable format such as ints, or
    # a dictionary, etc,  and handles known data type quirks
    normalised_pymongo_result = normalise_pymongo_result(raw_val)
    normalised_django = _normalise_django(django_val)

    _strip_django_defaults(normalised_pymongo_result, normalised_django)
    diffs = DeepDiff(
        normalised_pymongo_result,
        normalised_django,
        ignore_numeric_type_changes=True,
        ignore_order=True,
    )
    # at this point we should have 2 identical values, whether it's basic ints or a complex nested dictionary
    # if we don't then the model does not represent the database.
    if diffs:
        for category, items in diffs.items():
            for item in items:
                # instead of root, use the actual field name
                useable_item = str(item).replace("root", field_name, 1)
                value_mismatches.append(
                    f"[{model_class.__name__}] model error. Doc _id: {doc_id}\n"
                    f"  Db value does not match model value. {category} at {useable_item}"
                )

        # use pytest common/tests/hydration/[test_here].py -s --show-diffs for this to log
        # this is to make it almost impossible for any PII to get logged accidentally
        if show_diffs:
            logger.warning(doc_id)
            pretty = diffs.pretty()
            useable_pretty = str(pretty).replace("root", field_name, 1)
            logger.warning("Issue for document %s: \n %s", doc_id, useable_pretty)

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


def normalise_pymongo_result(val):
    """
    Ensures pymongo results  convert to predictable/standard data types. Then passes to generic normalising function.
    """
    # weird decimal mismatch  make it a normal decimal
    if isinstance(val, Decimal128):
        return val.to_decimal()

    return _normalise_common(val, normalise_pymongo_result)


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
            if _is_django_implicit_auto_pk(field):
                continue
            field_value = getattr(val, field.name)
            normalised_dict[field.column] = _normalise_django(field_value)
        return normalised_dict

    # regular top level primary key
    if hasattr(val, "_meta"):
        return _normalise_django(val.pk)

    return _normalise_common(val, _normalise_django)


def _strip_django_defaults(normalised_pymongo_result_val, django_val):
    """
    This removes false positives for data mismatches.
    In the database, even if a field is omitted, the django model will still give it a default value of "" or none.
    """
    if isinstance(normalised_pymongo_result_val, dict) and isinstance(django_val, dict):
        # Delete unmapped legacy primary key noise from pymongo result ('id', '_id') if not present in normalized Django
        # output
        for pk_key in ("id", "_id"):
            if pk_key in normalised_pymongo_result_val and pk_key not in django_val:
                del normalised_pymongo_result_val[pk_key]

        for key in list(django_val.keys()):
            # this does assume the default value
            if key not in normalised_pymongo_result_val and django_val[key] in (None, "", [], {}):
                del django_val[key]
            # recurse in case it's an embedded model that needs fixing
            elif key in normalised_pymongo_result_val:
                _strip_django_defaults(normalised_pymongo_result_val[key], django_val[key])

    # if it's an array of documents/models we need to recurse until it's removed all false positives
    elif isinstance(normalised_pymongo_result_val, list) and isinstance(django_val, list):
        for normalised_pymongo_result_doc, django_model in zip(normalised_pymongo_result_val, django_val, strict=False):
            _strip_django_defaults(normalised_pymongo_result_doc, django_model)
