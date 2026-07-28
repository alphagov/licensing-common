
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
