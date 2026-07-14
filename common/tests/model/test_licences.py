import pytest
from django.core.exceptions import ValidationError

from common.enums.countries import Countries, CountryCodes
from common.models.licences import AdministrativeArea, Licence, LicenceInteraction


def test_valid_admin_area():
    admin_area = AdministrativeArea(
        code=CountryCodes.ALL.value,
        countries=[Countries.NORTHERN_IRELAND.value, Countries.ENGLAND.value],
        name="NI,England",
    )

    admin_area.full_clean()
    assert admin_area.name == "NI,England"


def test_admin_area_country_invalid_throws_error():
    expected_error_message = "Invalid country"

    with pytest.raises(ValidationError) as e:
        admin_area = AdministrativeArea(
            code=CountryCodes.ALL.value,
            countries=["test"],
            name="test"
        )

        admin_area.full_clean()

    assert e.value.messages == [expected_error_message]


def test_admin_area_name_invalid_throws_error():
    expected_error_message = "Invalid name"
    with pytest.raises(ValidationError) as e:
        admin_area = AdministrativeArea(
            code=CountryCodes.ALL.value,
            countries=[Countries.NORTHERN_IRELAND.value],
            name="test"
        )

        admin_area.full_clean()

    assert e.value.messages == [expected_error_message]


def test_admin_area_code_invalid_throws_error():
    expected_error_message = "Invalid country code"
    with pytest.raises(ValidationError) as e:
        admin_area = AdministrativeArea(
            code="9",
            countries=[Countries.NORTHERN_IRELAND.value],
            name="NI"
        )
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
    expected_error_message = "Invalid interaction id"
    with pytest.raises(ValidationError) as e:
        interaction = LicenceInteraction(
            licence_interaction_name="test",
            interaction_id=1
        )

        interaction.full_clean()

    assert e.value.messages == [expected_error_message]

