import pytest

from common.tests.utils.db_utils import is_local_db_available


@pytest.fixture(autouse=True)
def check_db_online():
    """Runs automatically before every test in tests/hydration/."""
    if not is_local_db_available():
        pytest.skip("Local DocumentDB connection failed. Skipping test.")


@pytest.fixture(autouse=True)
def unblock_db_for_hydration_tests(django_db_blocker):
    """
    By default, pytest blocks calls to a db because it wants to make a test db.
    The hydration tests are designed to use a local database not spin up a test db.
    This function lifts the lock on database queries.
    @pytest.mark.django_db can't be used because that will sping up a test db.
    """
    with django_db_blocker.unblock():
        yield
