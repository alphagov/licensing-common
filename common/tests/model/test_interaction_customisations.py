import bson
import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from common.models.interaction_customisations import Customisation, InteractionCustomisation
from common.models.shared_models import PaymentAmount


def test_valid_interaction_customisation_without_customisations():
    interaction_customisation = InteractionCustomisation(
        authority_slug_url="test-slug",
        licence_code="test-code",
        interaction_id=0,
        interaction_sub_id=999,
    )

    interaction_customisation.full_clean()


def test_valid_interaction_customisation_with_customisation():
    customisation = Customisation(
        is_postal_allowed=False,
        number_of_days_to_process=30,
        is_processing_days_working_days=True,
        has_tacit_consent=False,
        created_at=timezone.now(),
        is_fee_required=True,
        fixed_fee_amount=PaymentAmount(pence=500),
        legislation_name="test-legislation",
        introduction_text="test-introduction",
        declarations=["test-declaration1", "test-declaration2"],
        department=bson.ObjectId(),
    )

    interaction_customisation = InteractionCustomisation(
        authority_slug_url="test-slug",
        licence_code="test-code",
        interaction_id=0,
        interaction_sub_id=999,
        pending_customisation=customisation,
    )

    interaction_customisation.full_clean()


def test_invalid_interaction_id_interaction_customisation_throws_error():
    expected_error_message = "'1' is not a valid Interaction Id."
    with pytest.raises(ValidationError) as e:
        interaction_customisation = InteractionCustomisation(
            authority_slug_url="test-slug",
            licence_code="test-code",
            interaction_id=1,
            interaction_sub_id=999,
        )

        interaction_customisation.full_clean()

    assert expected_error_message in e.value.messages
    assert len(e.value.messages) == 1
