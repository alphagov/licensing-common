from functools import lru_cache

from django.conf import settings
from pymongo import MongoClient


@lru_cache(maxsize=1)
def is_local_db_available() -> bool:
    """Checks if DocumentDB is reachable. Cached so it only pings once per run."""
    try:
        with MongoClient(settings.DOCUMENT_DB_CONN, serverSelectionTimeoutMS=500) as client:
            client.admin.command("ping")
            return True
    except Exception:
        return False
