import pytest
from django.core.exceptions import ValidationError
import re
from common.models.authorities import Authority, ContactDetails, LicenceDetails


@pytest.fixture
def make_license_details():
    def _factory(codes=None):
        codes = codes
        return [LicenceDetails(licence_code=code) for code in codes]
    return _factory

def test_invalid_snac_code_throws_error():
    expected_error_message = "Invalid entry: 'test' is not a valid snac code."

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
    expected_error_message = "Invalid entry: 'test' is not a valid country."

    with pytest.raises(ValidationError) as e:
        authority = Authority(
            url_slug="test",
            name="test",
            agency_id=1,
            full_name="test",
            authority_url="",
            snac_codes=["00AA"],
            countries=["test"],
            encoded_image="",
            licence_details=[
                LicenceDetails(
                    licence_code="Test",
                    offered_by_authority=True,
                    using_gov_uk=True,
                    authority_url="",
                )
            ],
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


def test_valid_authority(db_tracker, db_cleanup):
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

    db_tracker.register_created(authority._id)

    authority.save()

    db_cleanup(Authority, db_tracker.created_ids)


def test_cleanup_of_updated_model(db_tracker, db_cleanup):
    authority = Authority.objects.create(
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

    db_tracker.register_updated(authority._id, authority)
    Authority.objects.filter(_id=authority._id).update(name="test_update")

    updated_authority = Authority.objects.get(_id=authority._id)
    assert updated_authority.name == "test_update"

    db_cleanup(model=Authority, original_state=db_tracker.original_state)

    db_tracker.register_created(authority._id)
    db_cleanup(model=Authority, created_ids=db_tracker.created_ids)


def test_authority_id_returns_url_slug():
    authority = Authority(
        url_slug="test-url-slug",
    )
    assert authority.id == "test-url-slug"

def test_find_licence_detail_finds_licence_with_matching_code(mocker, make_license_details):
    expected_licence_code = "5151-5-1"
    authority = Authority(
        licence_details=  make_license_details(["1234-2-1", expected_licence_code,"3421-3-1"])
    )
    licence_detail = authority.find_licence_detail(expected_licence_code)
    assert licence_detail.licence_code == expected_licence_code

def test_find_licence_detail_throws_error_when_multiple_licences_found(make_license_details):
    expected_licence_code = "5151-5-1"
    authority = Authority(
        licence_details=  make_license_details(["1234-2-1", expected_licence_code,expected_licence_code])
    )
    expected_error_message = re.compile(r"multiple matching", re.IGNORECASE)
    with pytest.raises(RuntimeError, match=expected_error_message):
        authority.find_licence_detail(expected_licence_code)

def test_find_licence_detail_returns_none_when_no_licence_with_matching_code(make_license_details):
    non_existing_licence_code = "5151-5-1"
    authority = Authority(
        licence_details=  make_license_details(["1234-2-1", "2323-5-1", "3421-3-1"])
    )
    licence_detail = authority.find_licence_detail(non_existing_licence_code)
    assert licence_detail is None


def test_find_licence_detail_returns_none_when_empty_list():
    non_existing_licence_code = "5151-5-1"
    authority = Authority(
        licence_details= []
    )
    licence_detail = authority.find_licence_detail(non_existing_licence_code)
    assert licence_detail is None