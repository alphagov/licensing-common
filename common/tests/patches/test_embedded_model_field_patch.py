from copy import deepcopy

import pytest
from django.core.exceptions import ValidationError
from django.db import models
from django_mongodb_backend.fields import EmbeddedModelField
from django_mongodb_backend.models import EmbeddedModel


class GrandchildModel(EmbeddedModel):
    identifier = models.CharField(max_length=255)

    class Meta:
        app_label = "common"

    def __str__(self):
        return f"{self.identifier}"


class ChildModel(EmbeddedModel):
    identifier = models.CharField(max_length=255)
    nullable_grandchild = EmbeddedModelField(GrandchildModel, null=True, blank=True)
    required_grandchild = EmbeddedModelField(GrandchildModel)

    class Meta:
        app_label = "common"

    def __str__(self):
        return f"{self.identifier}"


class ParentModel(models.Model):
    identifier = models.CharField(max_length=255)
    nullable_child = EmbeddedModelField(ChildModel, null=True, blank=True)
    required_child = EmbeddedModelField(ChildModel)

    class Meta:
        app_label = "common"

    def __str__(self):
        return f"{self.identifier}"


grand_child = GrandchildModel(
    identifier="grandchild",
)

child = ChildModel(
    identifier="child", required_grandchild=deepcopy(grand_child), nullable_grandchild=deepcopy(grand_child)
)

parent = ParentModel(identifier="parent", required_child=deepcopy(child), nullable_child=deepcopy(child))


def test_upstream_django_mongodb_backend_is_still_broken(monkeypatch):
    """Verifies that the unpatched django_mongodb_backend library still a bug where nullable grandchildren can't be null

    When this is fixed upstream, this test will fail, meaning our patch is now unneeded.
    """
    monkeypatch.setattr(EmbeddedModelField, "validate", EmbeddedModelField._original_validate)
    local_parent = deepcopy(parent)
    local_parent.required_child.nullable_grandchild = None

    with pytest.raises(ValidationError, match="Expected instance of type .*GrandchildModel"):
        local_parent.full_clean()


def test_our_patch_allows_nullable_grandchildren_to_be_null():
    """Verifies that our patch fixes the django_mongodb_backend bug where nullable grandchildren can't be null"""
    local_parent = deepcopy(parent)
    local_parent.required_child.nullable_grandchild = None
    local_parent.full_clean()


def test_required_children_are_required_with_patch():
    """Verifies we haven't unintentionally allowed required fields to be null"""
    local_parent = deepcopy(parent)
    local_parent.required_child = None

    with pytest.raises(ValidationError, match="This field cannot be null."):
        local_parent.full_clean()
