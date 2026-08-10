import pytest
from django.core.exceptions import ValidationError

from common.models.authorities import Authority, ContactDetails, LicenceDetails


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
