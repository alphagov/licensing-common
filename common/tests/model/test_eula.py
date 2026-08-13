import bson
import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from common.models.eula import Eula


def test_valid_eula():
    eula = Eula(
        version="1.0",
        valid_from=timezone.now(),
        html_text="<p>This is an eula version</p>",
    )

    eula.full_clean()


def test_creating_new_eula_with_same_version_throws_error(db_tracker, db_cleanup):
    expected_error_message = "Eula with this Version already exists."
    pre_existing_eula = Eula.objects.create(
        _id=bson.ObjectId(),
        version="2.0",
        valid_from=timezone.now(),
        html_text="<p>This is an eula version</p>",
    )

    db_tracker.register_created(pre_existing_eula._id)

    with pytest.raises(ValidationError) as e:
        new_eula = Eula(
            _id=bson.ObjectId(),
            version="2.0",
            valid_from=timezone.now(),
            html_text="<p>This is an eula version, this should fail to create</p>",
        )

        new_eula.full_clean()

    assert expected_error_message in e.value.messages
    assert len(e.value.messages) == 1

    db_cleanup(Eula, db_tracker.created_ids)
