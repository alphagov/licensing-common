import warnings

from django.db import models
from pymongo.database import Database


def verify_model_against_collection(
    db: Database, model_class: type[models.Model], collection_name: str, sample_size=100
):
    """
    This function compares actual BSON documents from the database with a django model.
    The aim is to see if the models are missing columns or not hydrating correctly by comparing raw data to the model.
    The usefulness of the test depends entirely on having access to a db with data to sample.
    """

    # sample size checks
    sample_docs = list(db[collection_name].aggregate([{"$sample": {"size": sample_size}}]))
    actual_sample_size = len(sample_docs)
    assert actual_sample_size > 0, f"Collection '{collection_name}' has no data"
    if actual_sample_size < sample_size:
        warnings.warn(UserWarning(f"{sample_size} asked for, only {actual_sample_size} found."), stacklevel=2)

    # make sure it returns at least an empty array for mismatches
    mismatches = []

    # create a dictionary that maps database column names to django field names
    db_column_to_field = {}
    for field in model_class._meta.fields:
        db_column_to_field[field.column] = field.name

    # actual comparisons start here
    for doc in sample_docs:
        # check data exists in both
        doc_id = doc["_id"]
        try:
            django_obj = model_class.objects.get(pk=str(doc_id))
        except model_class.DoesNotExist:
            mismatches.append(f"[{model_class.__name__}] Doc _id={doc_id} missing in Django ORM.")
            continue

        # check every column on the document has a corresponding django model attribute
        for raw_key, raw_val in doc.items():
            if raw_key not in db_column_to_field.keys():
                mismatches.append(f"[{model_class.__name__}] Key '{raw_key}' in DB missing from Django model.")
                continue

            field_name = db_column_to_field[raw_key]
            django_val = getattr(django_obj, field_name)

            # to compare we need common ground, normalising the data gets both in a comparable format such as ints, or
            # a dictionary, etc,  and handles known data type quirks
            normalised_bson = normalise_bson(raw_val)
            normalised_django = normalise_django(django_val)

            # fixes issues caused by nosqls ability to omit entire columns
            remove_unwanted_default_values_from_django(normalised_bson, normalised_django)

            # at this point we should have 2 identical values, whether it's basic ints or a complex nested dictionary
            # if we don't then the model does not represent the database.
            if normalised_bson != normalised_django:
                mismatches.append(
                    f"[{model_class.__name__}] model error. Doc _id: {doc_id} | Field: '{field_name}'\n"
                    f"  Db value does not match model value."
                )
    return mismatches


def normalise_common(val, normaliser_fn):
    """
    Handles common cleaning tasks like forcing embedded documents/models to keep recursing through until all the
    primitive data attributes have been normalised
    """
    if val is None:
        return None

    # Make sure sets are predictable lists and recurse so child values are normalised too
    if isinstance(val, set):
        return sorted([normaliser_fn(item) for item in val], key=str)

    # Recurse so child values are normalised too, also converts tuples to a list
    if isinstance(val, (list, tuple)):
        items = [normaliser_fn(item) for item in val]
        # this catches edge cases where a django set gets compared to a bson list
        # it does this by ensuring primitive items always get sorted just in case. little inefficient
        if items and all(isinstance(x, (str, int, float, bool, type(None))) for x in items):
            return sorted(items, key=str)
        return items

    # If the value is a dictionary then recursion is needed to normalise values but maintain key names
    if isinstance(val, dict):
        return {k: normaliser_fn(v) for k, v in val.items()}

    # Removes whitespace generally but was initially due to one of the ideas containing a new line causing a false data
    # mismatch on objectids
    if type(val).__name__ == "ObjectId" or isinstance(val, str):
        return str(val).strip()

    return val


def normalise_bson(val):
    """
    Ensures bson data convert to predictable/standard data types before common cleaning tasks
    """
    # weird decimal mismatch by default on decimals, make it a normal decimal
    if type(val).__name__ == "Decimal128":
        return val.to_decimal()

    return normalise_common(val, normalise_bson)


def normalise_django(val):
    """
    Handles issues around embedded django models expecting primary keys
    if it's an embedded model it converts that model to a dictionary.
    Finally hands to the common cleaning tasks
    """
    if val is None:
        return None

    # if it has a _meta it has to be a django model of some kind
    if hasattr(val, "_meta"):
        # if the primary key is none it must be an embedded model as a top level model would have an objectid pk
        if getattr(val, "pk", None) is None:
            normalised_dict = {}
            for field in val._meta.fields:
                # Skip primary keys on embedded objects before they cause a mismatch
                if field.primary_key:
                    continue

                # Get the value from the Django model using the field's Python attribute name
                field_value = getattr(val, field.name)

                # Map the database column name to the normalised value
                normalised_dict[field.column] = normalise_django(field_value)

            return normalised_dict
        return normalise_django(val.pk)

    return normalise_common(val, normalise_django)


def remove_unwanted_default_values_from_django(bson_val, django_val):
    """
    This removes false positives for data mismatches.
    In the database, even if a field is omitted, the django model will still give it a default value of "" or none.
    """
    if isinstance(bson_val, dict) and isinstance(django_val, dict):
        for key in list(django_val.keys()):
            # this does assume the default value is either going to be none or empty string so it's  a bit fragile
            if django_val[key] in (None, "") and key not in bson_val:
                del django_val[key]
            elif key in bson_val:
                remove_unwanted_default_values_from_django(bson_val[key], django_val[key])

    # if it's an array of documents/models we need to recurse until it's removed all false positives
    elif isinstance(bson_val, list) and isinstance(django_val, list):
        for bson_doc, django_model in zip(bson_val, django_val, strict=True):
            remove_unwanted_default_values_from_django(bson_doc, django_model)
