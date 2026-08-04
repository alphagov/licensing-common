from bson import ObjectId
from django.db import models
from django_mongodb_backend.fields import EmbeddedModelField, ObjectIdField
from django_mongodb_backend.models import EmbeddedModel

from common.tests.utils.hydration import check_data_structure, check_values, map_columns_to_fields


class MockDepartment(models.Model):
    _id = ObjectIdField(primary_key=True)
    name = models.CharField(default="", max_length=255, blank=True)
    num_of_employees = models.IntegerField(db_column="numEmployees")
    is_mock = models.BooleanField(db_column="isMock")

    class Meta:
        app_label = "tests"
        managed = False

    def __str__(self):
        return self.name


ID = ObjectId()
NAME = "Department of mocks"
NUM_EMPLOYEES = 30
MOCK_DEPARTMENT_FIELDS = map_columns_to_fields(MockDepartment)

mock_django = MockDepartment(_id=ID, name=NAME, num_of_employees=NUM_EMPLOYEES, is_mock=True)
mock_bson = {"_id": ID, "name": NAME, "numEmployees": NUM_EMPLOYEES, "isMock": True}


def test_unnested_document_of_primitives_matches_model():
    # create bson representation

    # create django model
    for raw_key, raw_val in mock_bson.items():
        assert check_data_structure(MockDepartment, MOCK_DEPARTMENT_FIELDS, raw_key) is None
        assert check_values(MockDepartment, MOCK_DEPARTMENT_FIELDS, raw_key, raw_val, ID, mock_django) == []


def test_unnested_document_of_primitives_with_extra_column_compared_to_model_flags_mismatch():
    extra_column = "extra_column"
    mutated_bson = mock_bson.copy()
    mutated_bson[extra_column] = False
    mismatches = None
    for raw_key in mutated_bson:
        error = check_data_structure(MockDepartment, MOCK_DEPARTMENT_FIELDS, raw_key)
        if error is not None:
            mismatches = error
    assert extra_column in mismatches
    assert "missing" in mismatches


def test_unnested_document_of_primitives_with_different_value_to_model_flags_mismatch():
    mutated_bson = mock_bson.copy()
    mutated_bson["numEmployees"] = 22
    errors = []
    for raw_key, raw_val in mutated_bson.items():
        errors += check_values(MockDepartment, MOCK_DEPARTMENT_FIELDS, raw_key, raw_val, ID, mock_django)
    assert len(errors) == 1
    assert "num_of_employees" in errors[0]


def test_unnested_document_of_primitives_with_different_value_type_to_model_flags_mismatch():
    mutated_bson = mock_bson.copy()
    # now it should see a string versus an int and flag an issue
    mutated_bson["numEmployees"] = str(NUM_EMPLOYEES)
    errors = []
    for raw_key, raw_val in mutated_bson.items():
        errors += check_values(MockDepartment, MOCK_DEPARTMENT_FIELDS, raw_key, raw_val, ID, mock_django)
    assert len(errors) == 1
    assert "num_of_employees" in errors[0]


class MockNest3(EmbeddedModel):
    actual_val = models.CharField(db_column="actualVal")

    class Meta:
        app_label = "tests"
        managed = False


class MockNest2(EmbeddedModel):
    nest_three = EmbeddedModelField(MockNest3, db_column="nestThree")

    class Meta:
        app_label = "tests"
        managed = False


class MockNest1(EmbeddedModel):
    nest_two = EmbeddedModelField(MockNest2, db_column="nestTwo")

    class Meta:
        app_label = "tests"
        managed = False


class MockDepartmentUltraNest(MockDepartment):
    nest_one = EmbeddedModelField(MockNest1, db_column="nestOne")

    class Meta:
        app_label = "tests"
        managed = False


nested_bson = mock_bson.copy()
nested_bson["nestOne"] = {"nestTwo": {"nestThree": {"actualVal": 2}}}


def test_nested_values_can_match_embedded_models():
    mock_nested_department = MockDepartmentUltraNest(
        nest_one=MockNest1(
            nest_two=MockNest2(nest_three=MockNest3(actual_val=2)),
        ),
        num_of_employees=NUM_EMPLOYEES,
        name=NAME,
        _id=ID,
        is_mock=True,
    )
    errors = []
    for raw_key, raw_val in nested_bson.items():
        errors += check_values(
            MockDepartmentUltraNest,
            map_columns_to_fields(MockDepartmentUltraNest),
            raw_key,
            raw_val,
            ID,
            mock_nested_department,
        )
    assert len(errors) == 0


def test_nested_values_can_mismatch_embedded_models():
    mock_nested_department = MockDepartmentUltraNest(
        nest_one=MockNest1(
            nest_two=MockNest2(nest_three=MockNest3(actual_val=1)),
        ),
        num_of_employees=NUM_EMPLOYEES,
        name=NAME,
        _id=ID,
        is_mock=True,
    )
    errors = []
    for raw_key, raw_val in nested_bson.items():
        errors += check_values(
            MockDepartmentUltraNest,
            map_columns_to_fields(MockDepartmentUltraNest),
            raw_key,
            raw_val,
            ID,
            mock_nested_department,
        )
    assert len(errors) == 1
    assert "nest_one" in errors[0]
