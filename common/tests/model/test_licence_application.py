from datetime import timedelta

import pytest
from bson import ObjectId
from django.core.exceptions import ValidationError
from django.utils.timezone import now

from common.enums.interaction_id_codes import InteractionIdCodes
from common.enums.virus_check_status import VirusCheckStatus
from common.models.licence_application import ApplicationStatus, LicenceApplication, SupportingDocument
from common.models.shared_models import PaymentAmount, SupportingDocumentDefinition


def test_valid_licence_application():
    licence_application = LicenceApplication(
        applicant_email="test@test.com",
        authority="test",
        licence="test",
        supporting_documents_online=True,
        application_document=SupportingDocument(
            definition=SupportingDocumentDefinition(), _id=ObjectId(), virus_check_status=VirusCheckStatus.CLEAN.value
        ),
        licence_code="test",
        interaction_id=InteractionIdCodes.APPLY.value,
        interaction_sub_id=0,
        status=ApplicationStatus(data_available=False, is_being_processed=False, collected_by_authority=False),
        application_date=now(),
        application_reference="test",
        authority_application_reference="test",
        expected_processing_date=now() + timedelta(days=7),
        tacit_consent=False,
        required_payment_amount=PaymentAmount(),
        fee_required=False,
        variable_fee=False,
        payment_reference_id="test",
        application_main_form="test",
        collected_by="test@test.com",
        under_process_by="test@test.com",
    )
    licence_application.full_clean()


def test_invalid_interaction_id_in_licence_application_service_throws_error():
    expected_error_message = "Value 1 is not a valid choice."
    with pytest.raises(ValidationError) as e:
        licence_application = LicenceApplication(interaction_id=1)
        licence_application.full_clean()

    assert expected_error_message in e.value.message_dict["interaction_id"]


def test_is_virus_detected_in_file():
    clean_document = SupportingDocument(virus_check_status=VirusCheckStatus.CLEAN.value)
    assert clean_document.is_virus_detected_in_file is False

    infected_document = SupportingDocument(virus_check_status=VirusCheckStatus.FOUND_VIRUS.value)
    assert infected_document.is_virus_detected_in_file is True


def test_valid_virus_check_status():
    expected_error_message = "Value 'Ok' is not a valid choice."
    with pytest.raises(ValidationError) as e:
        document = SupportingDocument(virus_check_status="Ok")
        document.full_clean()

    assert expected_error_message in e.value.message_dict["virus_check_status"]
