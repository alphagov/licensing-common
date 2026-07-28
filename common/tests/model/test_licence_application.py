
from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils.timezone import now

from common.enums.virus_check_status import VirusCheckStatus
from common.models.licence_application import LicenceApplication, Service, SupportingDocument
from common.models.shared_models import PaymentAmount


def test_is_virus_detected_in_file():
     clean_document = SupportingDocument(virus_check_status=VirusCheckStatus.CLEAN.value)
     assert clean_document.is_virus_detected_in_file is False

     infected_document = SupportingDocument(virus_check_status=VirusCheckStatus.FOUND_VIRUS.value)
     assert infected_document.is_virus_detected_in_file is True

def test_valid_licence_application():
    licence_application = LicenceApplication(
        applicant_email="test",
        authority="test",
        licence="test",
        supporting_documents_online=True,
        application_document=SupportingDocument(),
        service=Service(),
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
        collected_by="test",
        under_process_by="test"
    )
    licence_application.full_clean()
