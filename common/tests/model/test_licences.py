import pytest
import re
from django.core.exceptions import ValidationError

from common.enums.countries import Countries, CountryCodes
from common.models.licences import AdministrativeArea, Licence, LicenceInteraction


@pytest.fixture
def make_licence_interactions():
    def _factory(interactions=None):
        return [LicenceInteraction(interaction_id= interaction_id, interaction_sub_id= interaction_sub_id) for interaction_id, interaction_sub_id in interactions]
    return _factory

def test_valid_admin_area():
    admin_area = AdministrativeArea(
        code=CountryCodes.ALL.value,
        countries=[Countries.NORTHERN_IRELAND.value, Countries.ENGLAND.value],
        name="NI,England",
    )

    admin_area.full_clean()
    assert admin_area.name == "NI,England"


def test_admin_area_country_invalid_throws_error():
    expected_error_message = "Invalid entry: 'test' is not a valid country."

    with pytest.raises(ValidationError) as e:
        admin_area = AdministrativeArea(code=CountryCodes.ALL.value, countries=["test"], name="test")

        admin_area.full_clean()

    assert e.value.messages == [expected_error_message]


def test_admin_area_name_invalid_throws_error():
    expected_error_message = "Invalid name"
    with pytest.raises(ValidationError) as e:
        admin_area = AdministrativeArea(
            code=CountryCodes.ALL.value, countries=[Countries.NORTHERN_IRELAND.value], name="test"
        )

        admin_area.full_clean()

    assert e.value.messages == [expected_error_message]


def test_admin_area_code_invalid_throws_error():
    expected_error_message = "Invalid country code."
    with pytest.raises(ValidationError) as e:
        admin_area = AdministrativeArea(code="9", countries=[Countries.NORTHERN_IRELAND.value], name="NI")
        admin_area.full_clean()

    assert e.value.messages == [expected_error_message]


def test_licence_interaction_invalid_consent_throws_error():
    expected_error_message = "Invalid consent"
    with pytest.raises(ValidationError) as e:
        interaction = LicenceInteraction(
            licence_interaction_name="test",
            tacit_consent="test",
        )

        interaction.full_clean()

    assert e.value.messages == [expected_error_message]


def test_licence_interaction_invalid_interaction_id_throws_error():
    expected_error_message = "'1' is not a valid Interaction Id."
    with pytest.raises(ValidationError) as e:
        interaction = LicenceInteraction(licence_interaction_name="test", interaction_id=1)

        interaction.full_clean()

    assert e.value.messages == [expected_error_message]


def test_licence_id_returns_licence_code():
    licence = Licence(
        licence_code="1234-5-6",
        name="test",
        legislation_name="test",
        url_slug="test",
        local_government_service_list_id="test",
        administrative_area=AdministrativeArea(
            code=CountryCodes.ALL.value,
            countries=[Countries.NORTHERN_IRELAND.value, Countries.ENGLAND.value],
            name="NI,England",
        ),
    )
    assert licence.id == "1234-5-6"


def test_find_licence_interaction_finds_interaction_only_when_both_ids_match(make_licence_interactions):
    expected_interaction_id = 15
    expected_sub_interaction_id = 2
    licence= Licence(
        licence_interactions =  make_licence_interactions([(expected_interaction_id, 1),
                                                           (expected_interaction_id, expected_sub_interaction_id),
                                                           (12, expected_sub_interaction_id)])
    )
    interaction = licence.find_interaction(expected_interaction_id, expected_sub_interaction_id)
    assert interaction.interaction_id == expected_interaction_id
    assert interaction.interaction_sub_id == expected_sub_interaction_id

def test_find_licence_interaction_throws_error_when_multiple_licences_found(make_licence_interactions):
    expected_interaction_id = 15
    expected_sub_interaction_id = 2
    licence= Licence(
        licence_interactions =  make_licence_interactions([(expected_interaction_id, expected_sub_interaction_id),
                                                           (expected_interaction_id, expected_sub_interaction_id),
                                                           (12, 1)])
    )
    expected_error_message = re.compile(r"multiple matching", re.IGNORECASE)
    with pytest.raises(RuntimeError, match=expected_error_message):
        interaction = licence.find_interaction(expected_interaction_id, expected_sub_interaction_id)

def test_find_licence_interaction_returns_none_when_no_licence_with_matching_code(make_licence_interactions):
    not_expected_interaction_id = 15
    not_expected_sub_interaction_id = 2
    licence= Licence(
        licence_interactions =  make_licence_interactions([(not_expected_interaction_id, 1),
                                                           (11, not_expected_sub_interaction_id),
                                                           (12, 1)])
    )
    interaction = licence.find_interaction(not_expected_interaction_id, not_expected_sub_interaction_id)
    assert interaction is None


def test_find_licence_interaction_returns_none_when_empty_list():
    not_expected_interaction_id = 15
    not_expected_sub_interaction_id = 2
    licence= Licence(
        licence_interactions =  []
    )
    interaction = licence.find_interaction(not_expected_interaction_id, not_expected_sub_interaction_id)
    assert interaction is None