import os
from enum import StrEnum

import clamd


class ScanResult(StrEnum):
    CLEAN = "OK"
    INFECTED = "FOUND"


class VirusScanner:
    def __init__(self):
        self.host = os.getenv("VIRUS_SCANNER_HOST")
        self.port = int(os.getenv("VIRUS_SCANNER_PORT", 3310))
        self.timeout = int(os.getenv("VIRUS_SCANNER_TIMEOUT", 5))
        self.connection = clamd.ClamdNetworkSocket(host=self.host, port=self.port, timeout=self.timeout)
        self.is_available = self.ping()

    def scan_file(self, stream):
        try:
            if not self.is_available:
                raise VirusScannerUnavailableError("Unable to connect to Virus Scanner")

            result = self.connection.instream(stream)["stream"]
            if ScanResult.CLEAN in result:
                return ScanResult.CLEAN
            return ScanResult.INFECTED
        except clamd.BufferTooLongError as e:
            raise FileTooLargeException("File is too large to virus scan") from e
        except clamd.ConnectionError as e:
            raise VirusScannerUnavailableError("A connection error occurred") from e

    def ping(self):
        response = self.connection.ping()
        return response == "PONG"


class VirusScannerUnavailableError(Exception):
    pass

class FileTooLargeException(Exception):
    pass