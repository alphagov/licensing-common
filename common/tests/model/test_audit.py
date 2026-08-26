from datetime import datetime

from common.models.audit import Audit


def test_string_of_audit_matches_expected_format():
    expected_string = (
        "[AuditEvent | Type: an_audit_type | Tags: tag: 1, another_tag: 2 "
        "| Detail: test data: older event, second test data: a second detail value | Hostname: host "
        "| Timestamp: 2012-12-03 12:04:00]"
    )
    tag_dict = {"tag": 1, "another_tag": 2}
    detail_dict = {"test data": "older event", "second test data": "a second detail value"}
    audit = Audit(
        audit_type="an_audit_type",
        tags=tag_dict,
        details=detail_dict,
        hostname="host",
        timestamp=datetime.strptime("2012-12-03 12:04:00", "%Y-%m-%d %H:%M:%S"),
    )
    assert expected_string == str(audit)
