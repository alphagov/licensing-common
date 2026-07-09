import pytest
from django.core.exceptions import ValidationError

from apply_for_a_licence.models.authorities import Authority, ContactDetails, LicenceDetails


def test_snac_codes_validation():
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
        )
        authority.clean_fields(exclude=[
            "url_slug",
            "name",
            "agency_id",
            "authority_url",
            "full_name",
            "licence_details",
            "contact_details",
            "countries"
            ])


def test_country_validation():
    expected_error_message = "Country is not valid"
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
        authority.clean_fields()
    print(e.value.messages)
    assert expected_error_message in e.value.messages

