import pytest
from django.db.models import Model
from django.forms.models import model_to_dict


@pytest.fixture
def db_tracker():
    class DBTracker:
        def __init__(self):
            self.created_ids = set()
            self.original_state = {}

        def register_created(self, record_id):
            self.created_ids.add(record_id)

        def register_updated(self, record_id, original_data):
            self.original_state[record_id] = original_data

    yield DBTracker()


@pytest.fixture
def db_cleanup():
    def _cleanup(model: Model, created_ids: set | None = None, original_state: dict | None = None):
        if created_ids is None:
            created_ids = set()

        if original_state is None:
            original_state = {}

        for record_id in created_ids:
            object_to_delete = model.objects.get(pk=record_id)
            object_to_delete.delete()

        for record_id, original_data in original_state.items():
            if record_id not in created_ids:
                data = model_to_dict(original_data)
                model.objects.filter(pk=record_id).update(**data)

    yield _cleanup
