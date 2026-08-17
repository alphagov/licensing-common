import logging
import warnings

from bson import Decimal128, ObjectId
from deepdiff import DeepDiff
from django.core.exceptions import ValidationError
from django.db import models
from django_mongodb_backend.models import EmbeddedModel
from pymongo.database import Database

logger = logging.getLogger(__name__)


def verify_model_against_collection(db: Database, model_class: type[models.Model], sample_size=0, show_diffs=False):
    """
    This function compares actual documents from the database (via pymongo)  with a django model and reports any issues.

    The aim is to see if the model is missing attributes, has incompatibility errors,  or not hydrating correctly. It
    compares documents to the model by using pymongo to pull "raw" data and using django to hydrate the equivalent
    model. It then converts both to dictionaries and compares the keys and values directly.

    This is designed to be used against a local database with data that is accurate to reality. Its main goal is to
    increase confidence in initial project release but can help detect database drift and bad data.
    """
    collection_name = model_class._meta.db_table

    if sample_size == 0:
        sample_docs = list(db[collection_name].find())
    else:
        sample_docs = list(db[collection_name].aggregate([{"$sample": {"size": sample_size}}]))

    actual_sample_size = len(sample_docs)
    if actual_sample_size == 0:
        raise ValueError(f"Collection '{collection_name}' has no data")
    else:
        if isinstance(sample_size, int) and actual_sample_size < sample_size:
            warnings.warn(
                f"{sample_size} asked for, only {actual_sample_size} found.",
                category=UserWarning,
                stacklevel=2,
            )
        if actual_sample_size < 100:
            warnings.warn(
                "Less than 100 items sampled, this may not be a fully representative data set.",
                category=UserWarning,
                stacklevel=2,
            )

    mismatches = _get_mismatches(model_class, sample_docs, show_diffs)
    logger.info(
        "[%s] Verified %s docs in '%s'. Found %s mismatch(es).",
        model_class.__name__,
        len(sample_docs),
        collection_name,
        len(mismatches),
    )
    return mismatches


def _get_mismatches(model_class: type[models.Model], sample_docs, show_diffs=False):
    mismatches = []

    db_attribute_to_django_field_dictionary = _get_explicitly_declared_attributes(model_class)
    real_primary_key_col = model_class._meta.pk.column

    for doc in sample_docs:
        displayable_doc_id = doc.get(real_primary_key_col) if show_diffs else doc.get("_id")
        try:
            django_obj = model_class.objects.get(pk=doc.get(real_primary_key_col))
        except model_class.DoesNotExist:
            mismatches.append(f"[{model_class.__name__}] Doc _id={displayable_doc_id} missing in Django ORM.")
            continue

        mismatches.extend(
            f"[{model_class.__name__}] Doc _id={displayable_doc_id}: {err}" for err in _get_clean_errors(django_obj)
        )

        for raw_attribute_key, raw_val in doc.items():
            # if there's an _id BUT we chose to use a different primary key, let's assume that exclusion is intended
            # and ignore the fact it's in the database and not on the model
            if (
                raw_attribute_key == "_id"
                and real_primary_key_col != "_id"
                and "_id" not in db_attribute_to_django_field_dictionary
            ):
                continue

            structure_mismatch = _get_data_structure_errors(
                model_class, db_attribute_to_django_field_dictionary, raw_attribute_key
            )
            if structure_mismatch:
                mismatches.append(structure_mismatch)
                continue

            field_name = db_attribute_to_django_field_dictionary[raw_attribute_key]
            mismatches.extend(
                _get_data_value_errors(model_class, field_name, raw_val, displayable_doc_id, django_obj, show_diffs)
            )
    return mismatches


def _get_clean_errors(django_obj):
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
    """
    This is a workaround designed to ignore any auto-injected django attributes, most notably false primary keys
    """
    return {field.column: field.name for field in model_class._meta.fields if not _is_django_implicit_auto_pk(field)}


def _get_data_structure_errors(model_class, db_attribute_to_field, document_attribute):
    """
    Returns an error message if there is no django property mapped to a document
    """
    if document_attribute not in db_attribute_to_field:
        return f"[{model_class.__name__}] Attribute '{document_attribute}' in DB missing from Django model."
    return None


def _get_data_value_errors(model_class, field_name, raw_val, doc_id, django_obj, show_diffs=False):
    value_mismatches = []
    django_val = getattr(django_obj, field_name)

    # the normalise functions remove the data noise and standardise both data to dictionaries
    pymongo_result_dictionary = normalise_pymongo_result(raw_val)
    django_model_data_dictionary = _normalise_django(django_val)

    _strip_django_defaults(pymongo_result_dictionary, django_model_data_dictionary)
    diffs = DeepDiff(
        pymongo_result_dictionary,
        django_model_data_dictionary,
        ignore_numeric_type_changes=True,
        ignore_order=True,
    )

    if diffs:
        value_mismatches = [
            f"[{model_class.__name__}] model error. Doc _id: {doc_id}\n"
            f"  Db value does not match model value. {category} at {str(item).replace('root', field_name, 1)}"
            for category, items in diffs.items()
            for item in items
        ]
        # this flag is to make it almost impossible for any PII to get logged accidentally
        if show_diffs:
            pretty = diffs.pretty()
            useable_pretty = str(pretty).replace("root", field_name, 1)
            logger.warning("Issue for document %s: \n %s", doc_id, useable_pretty)

    return value_mismatches


def _get_normalised_dictionary(val, normaliser_fn):
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

    return _get_normalised_dictionary(val, normalise_pymongo_result)


def _normalise_django(val):
    """
    Handles issues around embedded django models expecting primary keys.
    If it's an embedded model it converts that model to a dictionary skipping primary key.
    Finally hands to the common cleaning tasks
    """
    if val is None:
        return None

    # for embedded models, skip over autogenerated django primary keys
    if isinstance(val, EmbeddedModel):
        return {
            field.column: _normalise_django(getattr(val, field.name))
            for field in val._meta.fields
            if not _is_django_implicit_auto_pk(field)
        }

    if hasattr(val, "_meta"):  # if not embedded model
        return _normalise_django(val.pk)

    return _get_normalised_dictionary(val, _normalise_django)


def _strip_django_defaults(normalised_pymongo_result_val, django_val):
    """
    This removes false positives for data mismatches.
    In the database, even if a field is omitted, the django model will still give it a default value of "" or none.
    """
    if isinstance(normalised_pymongo_result_val, dict) and isinstance(django_val, dict):
        # Delete unmapped legacy primary key noise from pymongo result ('id', '_id') if not present on django model
        for pk_key in ("id", "_id"):
            if pk_key in normalised_pymongo_result_val and pk_key not in django_val:
                del normalised_pymongo_result_val[pk_key]

        for key in list(django_val.keys()):
            if key not in normalised_pymongo_result_val and django_val[key] in (None, "", [], {}):
                del django_val[key]
            # recurse in case it's an embedded model that needs fixing
            elif key in normalised_pymongo_result_val:
                _strip_django_defaults(normalised_pymongo_result_val[key], django_val[key])

    # if it's an array of documents/models we need to recurse until it's removed all false positives
    elif isinstance(normalised_pymongo_result_val, list) and isinstance(django_val, list):
        for normalised_pymongo_result_doc, django_model in zip(normalised_pymongo_result_val, django_val, strict=False):
            _strip_django_defaults(normalised_pymongo_result_doc, django_model)
