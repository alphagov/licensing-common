import os
import tempfile
import time
import socket

import clamd
import pytest

from common.services.virus_scanner import VirusScanner, ScanResult, FileTooLargeException, VirusScannerUnavailableError

"""
These tests run against a ClamAV container running in Docker, ensure container is up and running
"""

@pytest.fixture(scope="session", autouse=True)
def wait_for_clam_av():
        host = os.getenv("VIRUS_SCANNER_HOST", "localhost")
        port = int(os.getenv("VIRUS_SCANNER_PORT", "3310"))
        timeout_seconds = 180.0
        poll_interval = 1.0
        deadline = time.monotonic() + timeout_seconds
        last_error = None

        while time.monotonic() < deadline:
            try:
                with socket.create_connection((host, port), timeout=2.0) as sock:
                    sock.settimeout(2.0)
                    sock.sendall(b"zPING\x00")
                    reply = sock.recv(64)
                    if b"PONG" in reply:
                        return
                    last_error = f"Unexpected reply: {reply!r}"
            except OSError as exc:
                last_error = exc

            time.sleep(poll_interval)

        pytest.fail(
            f"ClamAV at {host}:{port} did not respond with PONG within "
            f"{timeout_seconds}s. Last error: {last_error}"
        )


def test_virus_scanner_connection_ping(wait_for_clam_av):
    scanner = VirusScanner()
    assert scanner.ping()


def test_scan_files_throws_error_scanner_unavailable(wait_for_clam_av):
    scanner = VirusScanner()
    scanner.is_available = False

    with pytest.raises(VirusScannerUnavailableError):
        with open("common/tests/resources/Fish_Dealers_Licence.pdf", "rb") as f:
            scanner.scan_file(f)


def test_scan_files_returns_ok_result_when_scanning_clean_file(wait_for_clam_av):
    scanner = VirusScanner()
    with open("common/tests/resources/Fish_Dealers_Licence.pdf", "rb") as f:
        result = scanner.scan_file(f)
    assert result == ScanResult.CLEAN


def test_scan_files_returns_infected_when_scanning_infected_file(wait_for_clam_av):
    scanner = VirusScanner()
    with tempfile.TemporaryFile(mode="w+b") as file:
        file.write(b"X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR" + b"-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*")
        file.seek(0)
        result = scanner.scan_file(file)
    assert result == ScanResult.INFECTED


def test_scan_files_handles_buffer_too_long_exception(mocker, wait_for_clam_av):
    scanner = VirusScanner()
    mocker.patch.object(scanner.connection, "instream", side_effect=clamd.BufferTooLongError())

    with pytest.raises(FileTooLargeException):
        with open("common/tests/resources/Fish_Dealers_Licence.pdf", "rb") as f:
            scanner.scan_file(f)


def test_scan_files_handles_connection_exception(mocker, wait_for_clam_av):
    scanner = VirusScanner()
    mocker.patch.object(scanner.connection, "instream", side_effect=clamd.ConnectionError())

    with pytest.raises(VirusScannerUnavailableError) as e:
        with open("common/tests/resources/Fish_Dealers_Licence.pdf", "rb") as f:
            scanner.scan_file(f)

        assert e.value.args[0] == "A connection error occurred"