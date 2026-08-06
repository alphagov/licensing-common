from django.db import models
from django_mongodb_backend.fields import EmbeddedModelArrayField, EmbeddedModelField, ObjectIdField
from django_mongodb_backend.models import EmbeddedModel


class MockDepartment(models.Model):
    """
    Simple flat model with primitives only
    """

    _id = ObjectIdField(primary_key=True)
    name = models.CharField(default="", max_length=255, blank=True)
    num_of_employees = models.IntegerField(db_column="numEmployees")
    is_mock = models.BooleanField(db_column="isMock")

    class Meta:
        app_label = "tests"
        managed = False

    def __str__(self):
        return self.name


class MockNestWithValue(EmbeddedModel):
    """
    The bottom of nesting where actual value lives
    """

    actual_val = models.CharField(db_column="actualVal")

    class Meta:
        app_label = "tests"
        managed = False


class MockNest2(EmbeddedModel):
    """
    Purely a vehicle for later nesting
    """

    MockNestWithValue = EmbeddedModelField(MockNestWithValue, db_column="mockNestWithValue")

    class Meta:
        app_label = "tests"
        managed = False


class MockNest1(EmbeddedModel):
    """
    Purely a vehicle for later nesting
    """

    nest_two = EmbeddedModelField(MockNest2, db_column="nestTwo")

    class Meta:
        app_label = "tests"
        managed = False


class MockDepartmentUltraNest(MockDepartment):
    """
    MockDepartment with horrific nesting chain
    """

    nest_one = EmbeddedModelField(MockNest1, db_column="nestOne")

    class Meta:
        app_label = "tests"
        managed = False


class MockDepartmentWithArrayList(MockDepartment):
    """
    Allows for testing on nested object lists
    """

    array_list = EmbeddedModelArrayField(MockNestWithValue, db_column="arrayList")

    class Meta:
        app_label = "tests"
        managed = False
