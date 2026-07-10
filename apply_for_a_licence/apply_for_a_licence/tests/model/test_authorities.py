import pytest
from django.core.exceptions import ValidationError

from apply_for_a_licence.models.authorities import Authority, ContactDetails, LicenceDetails


def test_invalid_snac_code_throws_error():
    expected_error_message = "Snac codes not valid"

    with pytest.raises(ValidationError) as e:
        authority = Authority(
            url_slug="test",
            name="test",
            full_name="test",
            agency_id=1,
            authority_url="",
            snac_codes=["test"],
            countries=[],
            encoded_image="test",
            licence_details=[],
            contact_details=ContactDetails(),
        )
        authority.clean_fields(exclude=["countries"])

    assert expected_error_message in e.value.messages


def test_invalid_country_throws_error():
    expected_error_message = "Invalid country"

    with pytest.raises(ValidationError) as e:
        authority=Authority(
            url_slug="test",
            name="test",
            agency_id=1,
            full_name="test",
            authority_url="",
            snac_codes=["00AA"],
            countries=["TEST"],
            encoded_image="",
            licence_details=[LicenceDetails(
                licence_code="Test",
                offered_by_authority=True,
                using_gov_uk=True,
                authority_url="",

            )],
            contact_details=ContactDetails(),
        )

        authority.full_clean()

    assert expected_error_message in e.value.messages


def test_snac_codes_can_be_empty():
    authority = Authority(
        url_slug="test",
        name="test",
        full_name="test",
        agency_id=1,
        authority_url="",
        snac_codes=[],
        countries=["England", "NI", "Scotland", "Wales"],
        encoded_image="",
        licence_details=[LicenceDetails(licence_code="Test", offered_by_authority=False, using_gov_uk=False)],
        contact_details=ContactDetails(),
    )
    authority.full_clean()

def test_valid_authority():
    authority = Authority(
        url_slug="test",
        name="test",
        full_name="test",
        agency_id=1,
        authority_url="",
        snac_codes=["00AA"],
        countries=["England", "NI", "Scotland", "Wales"],
        encoded_image="",
        licence_details=[LicenceDetails(licence_code="Test", offered_by_authority=False, using_gov_uk=False)],
        contact_details=ContactDetails(),
    )
    authority.full_clean()

