import pytest
from bson import ObjectId

from common.tests.utils.hydration import (
    _get_data_structure_errors,
    _get_data_value_errors,
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

    # A little overloaded as it's technically testing structure code, and multiple primitive matches, but it's
    # offsetting all the unhappy path tests below

    for raw_key, raw_val in mock_pymongo_result.items():
        assert (
            _get_data_structure_errors(
                model_class=MockDepartment, db_attribute_to_field=MOCK_DEPARTMENT_FIELDS, document_attribute=raw_key
            )
            is None
        )
        field_name = MOCK_DEPARTMENT_FIELDS[raw_key]
        assert (
            _get_data_value_errors(
                model_class=MockDepartment,
                field_name=field_name,
                raw_val=raw_val,
                doc_id=doc_id,
                django_obj=mock_django,
            )
            == []
        )


def test_get_data_structure_errors_detects_missing_attribute():
    extra_attribute = "extra_attribute"
    mismatch = _get_data_structure_errors(
        model_class=MockDepartment, db_attribute_to_field=MOCK_DEPARTMENT_FIELDS, document_attribute=extra_attribute
    )
    assert extra_attribute in mismatch
    assert "missing" in mismatch


def test_get_data_value_errors_detects_value_mismatch(mock_django, doc_id):
    mismatches = _get_data_value_errors(
        model_class=MockDepartment,
        field_name="num_of_employees",
        raw_val=NUM_EMPLOYEES + 1,
        doc_id=doc_id,
        django_obj=mock_django,
    )
    assert len(mismatches) == 1
    assert "num_of_employees" in mismatches[0]
    assert "values_changed" in mismatches[0]


def test_get_data_value_errors_detects_none_vs_value_mismatch(mock_django, doc_id):
    """
    Test get_data_value_errors() can detect errors where db is null and django is specifying a non-standard default
    value instead of "" or None.
    """
    mismatches = _get_data_value_errors(
        model_class=MockDepartment, field_name="name", raw_val=None, doc_id=doc_id, django_obj=mock_django
    )

    assert len(mismatches) == 1
    assert "type_changes" in mismatches[0] or "values_changed" in mismatches[0]
    assert "name" in mismatches[0]


def test_get_data_value_errors_detects_value_type_mismatch(mock_django, doc_id):
    """
    Test get_data_value_errors() detects different value types even if the values are logically equivalent like 2 and
    two.
    """
    mismatches = _get_data_value_errors(
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
    # A little overloaded as it's technically testing structure code and value code, but it's offsetting all the unhappy
    # path tests below

    mock_pymongo_result["nestOne"] = {"nestTwo": {"mockNestWithValue": {"actualVal": 2}}}
    for raw_key, raw_val in mock_pymongo_result.items():
        assert (
            _get_data_structure_errors(
                model_class=MockDepartmentUltraNest,
                db_attribute_to_field=MOCK_DEPARTMENT_ULTRA_NEST_FIELDS,
                document_attribute=raw_key,
            )
            is None
        )
        field_name = MOCK_DEPARTMENT_ULTRA_NEST_FIELDS[raw_key]
        assert (
            _get_data_value_errors(
                model_class=MockDepartmentUltraNest,
                field_name=field_name,
                raw_val=raw_val,
                doc_id=doc_id,
                django_obj=mock_department_ultra_nest,
            )
            == []
        )


def test_nested_pymongo_result_value_mismatches_detectable(mock_pymongo_result, doc_id, mock_department_ultra_nest):
    # This does depend on test_check_data_values_detects_value_type_mismatch() passing to be useful data

    mock_pymongo_result["nestOne"] = {"nestTwo": {"mockNestWithValue": {"actualVal": "2"}}}
    mismatches = []
    for raw_key, raw_val in mock_pymongo_result.items():
        field_name = MOCK_DEPARTMENT_ULTRA_NEST_FIELDS[raw_key]
        mismatches += _get_data_value_errors(
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
    pymongo_result_data = {}
    django_data = {"displayTitle": "", "defaultDeclarations": []}

    _strip_django_defaults(pymongo_result_data, django_data)

    assert django_data == {}


def test_strip_django_defaults_doesnt_remove_mismatched_defaults_when_actual_mismatch():
    pymongo_result_data = {"form": {"name": "Street Form", "version": 1}}
    django_data = {"form": {}}

    # shouldn't remove that form because document data exists so it's a proper mismatch
    _strip_django_defaults(pymongo_result_data, django_data)

    assert "form" in django_data
    assert django_data["form"] == {}


def test_get_data_value_errors_detects_data_loss_on_embedded_model(doc_id, mock_department_ultra_nest):
    raw_pymongo_result_val = {"nestTwo": {"mockNestWithValue": {"actualVal": 42}}}

    django_obj_with_unhydrated_child = MockDepartmentUltraNest(nest_one=MockNest1())

    mismatches = _get_data_value_errors(
        model_class=MockDepartmentUltraNest,
        field_name="nest_one",
        raw_val=raw_pymongo_result_val,
        doc_id=doc_id,
        django_obj=django_obj_with_unhydrated_child,
    )

    assert len(mismatches) > 0
    assert "Db value does not match model value" in mismatches[0]
    assert "nest_one" in mismatches[0]


def test_get_data_value_errors_ignores_matching_arrays(doc_id):
    array_list_pymongo_result = [
        {"actualVal": "one"},
        {"actualVal": "two"},
    ]

    django_obj = MockDepartmentWithArrayList(
        array_list=[MockNestWithValue(actual_val="one"), MockNestWithValue(actual_val="two")]
    )

    field_name = MOCK_DEPARTMENT_WITH_ARRAY_LIST_FIELDS["arrayList"]
    mismatches = _get_data_value_errors(
        model_class=MockDepartmentWithArrayList,
        field_name=field_name,
        raw_val=array_list_pymongo_result,
        doc_id=doc_id,
        django_obj=django_obj,
    )
    assert len(mismatches) == 0


def test_get_data_value_errors_detects_array_length_mismatch():
    three_pymongo_results = [
        {"actualVal": "one"},
        {"actualVal": "two"},
        {"actualVal": "three"},
    ]

    django_obj_with_two_array_items = MockDepartmentWithArrayList(
        array_list=[MockNestWithValue(actual_val="one"), MockNestWithValue(actual_val="two")]
    )
    field_name = MOCK_DEPARTMENT_WITH_ARRAY_LIST_FIELDS["arrayList"]
    mismatches = _get_data_value_errors(
        model_class=MockDepartmentWithArrayList,
        field_name=field_name,
        raw_val=three_pymongo_results,
        doc_id="mock_id_array_test",
        django_obj=django_obj_with_two_array_items,
    )
    assert len(mismatches) == 1
    assert "iterable_item_removed at array_list[2]" in mismatches[0]


def test_get_data_value_errors_detects_item_value_mismatch_inside_array(doc_id):
    """
    Test check_data_values() detects when arrays are the same length but don't contain the same data
    """
    array_list_pymongo_result = [{"actualVal": "one"}, {"actualVal": "wrong_value"}]
    django_obj = MockDepartmentWithArrayList(
        array_list=[MockNestWithValue(actual_val="one"), MockNestWithValue(actual_val="two")]
    )

    field_name = MOCK_DEPARTMENT_WITH_ARRAY_LIST_FIELDS["arrayList"]
    mismatches = _get_data_value_errors(
        model_class=MockDepartmentWithArrayList,
        field_name=field_name,
        raw_val=array_list_pymongo_result,
        doc_id=doc_id,
        django_obj=django_obj,
    )

    assert len(mismatches) == 1
    assert "values_changed" in mismatches[0]
    assert "array_list[1]" in mismatches[0]


def test_get_data_value_errors_detects_missing_nested_properties(doc_id, mock_department_ultra_nest):
    nested_pymongo_result_val = {
        "nestTwo": {
            "mockNestWithValue": {
                "actualVal": 2,
                "unknownSubKey": "lost_data",
            }
        }
    }

    mismatches = _get_data_value_errors(
        model_class=MockDepartmentUltraNest,
        field_name="nest_one",
        raw_val=nested_pymongo_result_val,
        doc_id=doc_id,
        django_obj=mock_department_ultra_nest,
    )

    assert len(mismatches) == 1
    assert "dictionary_item_removed" in mismatches[0]
    assert "nest_one" in mismatches[0]
