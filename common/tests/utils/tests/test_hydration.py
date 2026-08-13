import pytest
from bson import ObjectId

from common.tests.utils.hydration import (
    _check_data_structure,
    _check_data_values,
    _get_explicitly_declared_attributes,
    _strip_django_defaults,
)
from common.tests.utils.tests.hydration_classes_for_testing import (
    MockDepartment,
    MockDepartmentUltraNest,
    MockDepartmentWithArrayList,
    MockNest1,
    MockNest2,
    MockNestWithValue,
)

NAME = "Department of Mocks"
NUM_EMPLOYEES = 30
MOCK_DEPARTMENT_FIELDS = _get_explicitly_declared_attributes(MockDepartment)
MOCK_DEPARTMENT_ULTRA_NEST_FIELDS = _get_explicitly_declared_attributes(MockDepartmentUltraNest)
MOCK_DEPARTMENT_WITH_ARRAY_LIST_FIELDS = _get_explicitly_declared_attributes(MockDepartmentWithArrayList)


@pytest.fixture
def mock_django(doc_id):
    return MockDepartment(_id=doc_id, name=NAME, num_of_employees=NUM_EMPLOYEES, is_mock=True)


@pytest.fixture
def mock_pymongo_result(doc_id):
    return {"_id": doc_id, "name": NAME, "numEmployees": NUM_EMPLOYEES, "isMock": True}


@pytest.fixture
def doc_id():
    return ObjectId()


@pytest.fixture
def mock_department_ultra_nest(doc_id):
    return MockDepartmentUltraNest(
        nest_one=MockNest1(
            nest_two=MockNest2(MockNestWithValue=MockNestWithValue(actual_val=2)),
        ),
        num_of_employees=NUM_EMPLOYEES,
        name=NAME,
        _id=doc_id,
        is_mock=True,
    )


def test_unnested_document_of_primitives_and_matching_django_model_has_no_mismatches(
    mock_pymongo_result, mock_django, doc_id
):
    """
    Test a Django model that matches a document model doesn't find false mismatches.

    A little overloaded as it's technically testing structure code, and multiple primitive matches, but it's
    offsetting all the unhappy path tests below
    """
    for raw_key, raw_val in mock_pymongo_result.items():
        assert (
            _check_data_structure(
                model_class=MockDepartment, db_attribute_to_field=MOCK_DEPARTMENT_FIELDS, raw_key=raw_key
            )
            is None
        )
        field_name = MOCK_DEPARTMENT_FIELDS[raw_key]
        assert (
            _check_data_values(
                model_class=MockDepartment,
                field_name=field_name,
                raw_val=raw_val,
                doc_id=doc_id,
                django_obj=mock_django,
            )
            == []
        )


def test_check_data_structure_detects_missing_attribute():
    """
    Test check_data_structure() correctly finds cases where the document has extra attributes compared to the django
    model.

    This functionality catches missed mappings (or bad data).
    """
    extra_attribute = "extra_attribute"
    mismatch = _check_data_structure(
        model_class=MockDepartment, db_attribute_to_field=MOCK_DEPARTMENT_FIELDS, raw_key=extra_attribute
    )
    assert extra_attribute in mismatch
    assert "missing" in mismatch


def test_check_data_values_detects_value_mismatch(mock_django, doc_id):
    """
    Test check_data_values() correctly finds cases where the documents value and the django value don't match.
    """
    mismatches = _check_data_values(
        model_class=MockDepartment,
        field_name="num_of_employees",
        raw_val=NUM_EMPLOYEES + 1,
        doc_id=doc_id,
        django_obj=mock_django,
    )
    assert len(mismatches) == 1
    assert "num_of_employees" in mismatches[0]
    assert "values_changed" in mismatches[0]


def test_check_data_values_detects_none_vs_value_mismatch(mock_django, doc_id):
    """
    Test check_data_values() can detect errors where db is null and django is specifying a non-standard default value
    instead of "" or None.

    This is a useful feature because it can catch unintended data corruption from loading a null database value and
    then on save, giving it a default value that looks like real data.
    """
    # DB has null, Django hydrated a default string
    mismatches = _check_data_values(
        model_class=MockDepartment, field_name="name", raw_val=None, doc_id=doc_id, django_obj=mock_django
    )

    assert len(mismatches) == 1
    assert "type_changes" in mismatches[0] or "values_changed" in mismatches[0]
    assert "name" in mismatches[0]


def test_check_data_values_detects_value_type_mismatch(mock_django, doc_id):
    """
    Test check_data_values() detects different value types even if the values are logically equivalent like 2 and two.
    """
    mismatches = _check_data_values(
        model_class=MockDepartment,
        field_name="num_of_employees",
        raw_val=str(NUM_EMPLOYEES),
        doc_id=doc_id,
        django_obj=mock_django,
    )

    assert len(mismatches) == 1
    assert "type_changes" in mismatches[0]
    assert "num_of_employees" in mismatches[0]


def test_nested_pymongo_result_values_can_match_embedded_models(
    mock_pymongo_result, doc_id, mock_department_ultra_nest
):
    """
    Test documents with embedded documents that match django models with embedded models cause no mismatches.

    A little overloaded as it's technically testing structure code and value code, but it's offsetting all the unhappy
    path tests below
    """

    mock_pymongo_result["nestOne"] = {"nestTwo": {"mockNestWithValue": {"actualVal": 2}}}
    for raw_key, raw_val in mock_pymongo_result.items():
        assert (
            _check_data_structure(
                model_class=MockDepartmentUltraNest,
                db_attribute_to_field=MOCK_DEPARTMENT_ULTRA_NEST_FIELDS,
                raw_key=raw_key,
            )
            is None
        )
        field_name = MOCK_DEPARTMENT_ULTRA_NEST_FIELDS[raw_key]
        assert (
            _check_data_values(
                model_class=MockDepartmentUltraNest,
                field_name=field_name,
                raw_val=raw_val,
                doc_id=doc_id,
                django_obj=mock_department_ultra_nest,
            )
            == []
        )


def test_nested_pymongo_result_value_mismatches_detectable(mock_pymongo_result, doc_id, mock_department_ultra_nest):
    """
    Test that mismatches can be found even if the mismatch is deeply embedded.

    This does depend on test_check_data_values_detects_value_type_mismatch() passing to be useful data
    """
    mock_pymongo_result["nestOne"] = {"nestTwo": {"mockNestWithValue": {"actualVal": "2"}}}
    mismatches = []
    for raw_key, raw_val in mock_pymongo_result.items():
        field_name = MOCK_DEPARTMENT_ULTRA_NEST_FIELDS[raw_key]
        mismatches += _check_data_values(
            model_class=MockDepartmentUltraNest,
            field_name=field_name,
            raw_val=raw_val,
            doc_id=doc_id,
            django_obj=mock_department_ultra_nest,
        )
    assert len(mismatches) == 1
    assert "type_changes" in mismatches[0]
    assert "nest_one" in mismatches[0]


def test_strip_django_defaults_removes_irrelevant_defaults():
    """
    Test that strip_django_defaults() removes irrelevant defaults.

    Documents can omit attributes entirely. Django models can't omit the existence of a property so instead it has a
    default value for those properties. When comparing data, however, we don't want to falsely flag the difference
    when the database has literally nothing and Django has "". That's a limitation of mapping nosql in Django that
    can't be easily solved.
    """
    pymongo_result_data = {}
    django_data = {"displayTitle": "", "defaultDeclarations": []}

    _strip_django_defaults(pymongo_result_data, django_data)

    # should remove sparse keys from django_data so no diff is raised
    assert django_data == {}


def test_strip_django_defaults_doesnt_remove_mismatched_defaults():
    """
    Test strip_django_defaults() doesn't remove genuine mismatches when the db has values and the Django model has
    not been hydrated correctly.
    """
    pymongo_result_data = {"form": {"name": "Street Form", "version": 1}}
    django_data = {"form": {}}

    # shouldn't remove that form because document data exists so it's a proper mismatch
    _strip_django_defaults(pymongo_result_data, django_data)

    assert "form" in django_data
    assert django_data["form"] == {}


def test_check_data_values_detects_data_loss_on_embedded_model(doc_id, mock_department_ultra_nest):
    """
    Test check_data_values() flags data loss when db contains nested data but the Django embedded model fails to
    hydrate child fields.
    """
    # 1. MongoDB has populated nested data for 'nestOne'
    raw_pymongo_result_val = {"nestTwo": {"mockNestWithValue": {"actualVal": 42}}}

    # Django model has nest_one initialized but child data didn't hydrate
    django_obj = MockDepartmentUltraNest(nest_one=MockNest1())

    # Check values for the 'nest_one' field
    mismatches = _check_data_values(
        model_class=MockDepartmentUltraNest,
        field_name="nest_one",
        raw_val=raw_pymongo_result_val,
        doc_id=doc_id,
        django_obj=django_obj,
    )

    assert len(mismatches) > 0
    assert "Db value does not match model value" in mismatches[0]
    assert "nest_one" in mismatches[0]


def test_check_data_values_ignores_matching_arrays(doc_id):
    """
    Test check_data_values ignores when arrays match correctly.
    """
    array_list_pymongo_result = [
        {"actualVal": "one"},
        {"actualVal": "two"},
    ]

    django_obj = MockDepartmentWithArrayList(
        array_list=[MockNestWithValue(actual_val="one"), MockNestWithValue(actual_val="two")]
    )

    field_name = MOCK_DEPARTMENT_WITH_ARRAY_LIST_FIELDS["arrayList"]
    mismatches = _check_data_values(
        model_class=MockDepartmentWithArrayList,
        field_name=field_name,
        raw_val=array_list_pymongo_result,
        doc_id=doc_id,
        django_obj=django_obj,
    )
    assert len(mismatches) == 0


def test_check_data_values_detects_array_length_mismatch():
    """
    Test check_data_values() correctly detects when an array is missing an item.
    """
    # 3  items in pymongo result
    array_list_pymongo_result = [
        {"actualVal": "one"},
        {"actualVal": "two"},
        {"actualVal": "three"},
    ]

    # 2 django items
    django_obj = MockDepartmentWithArrayList(
        array_list=[MockNestWithValue(actual_val="one"), MockNestWithValue(actual_val="two")]
    )
    field_name = MOCK_DEPARTMENT_WITH_ARRAY_LIST_FIELDS["arrayList"]
    mismatches = _check_data_values(
        model_class=MockDepartmentWithArrayList,
        field_name=field_name,
        raw_val=array_list_pymongo_result,
        doc_id="mock_id_array_test",
        django_obj=django_obj,
    )
    assert len(mismatches) == 1
    assert "iterable_item_removed at array_list[2]" in mismatches[0]


def test_check_data_values_detects_item_value_mismatch_inside_array(doc_id):
    """
    Test check_data_values() detects when arrays are the same length but don't contain the same data
    """
    array_list_pymongo_result = [{"actualVal": "one"}, {"actualVal": "wrong_value"}]
    django_obj = MockDepartmentWithArrayList(
        array_list=[MockNestWithValue(actual_val="one"), MockNestWithValue(actual_val="two")]
    )

    field_name = MOCK_DEPARTMENT_WITH_ARRAY_LIST_FIELDS["arrayList"]
    mismatches = _check_data_values(
        model_class=MockDepartmentWithArrayList,
        field_name=field_name,
        raw_val=array_list_pymongo_result,
        doc_id=doc_id,
        django_obj=django_obj,
    )

    assert len(mismatches) == 1
    assert "values_changed" in mismatches[0]
    assert "array_list[1]" in mismatches[0]


def test_check_data_values_detects_missing_nested_properties(doc_id, mock_department_ultra_nest):
    """
    Test check_data_values() detects missing sub-properties inside nested models.

    Check_data_structure() guards against unmapped top-level document attributes, check_data_values() relies on DeepDiff
    to recursively inspect embedded models and flag missing keys that are nested lower down.
    """
    nested_pymongo_result_val = {
        "nestTwo": {
            "mockNestWithValue": {
                "actualVal": 2,
                "unknownSubKey": "lost_data",
            }
        }
    }

    mismatches = _check_data_values(
        model_class=MockDepartmentUltraNest,
        field_name="nest_one",
        raw_val=nested_pymongo_result_val,
        doc_id=doc_id,
        django_obj=mock_department_ultra_nest,
    )

    assert len(mismatches) == 1
    assert "dictionary_item_removed" in mismatches[0]
    assert "nest_one" in mismatches[0]
