from django.db import models


# Check tests for concrete example of issue being patched
def patch_django_mongodb_backend_to_accept_nullable_nested_embedded_models():
    """
    Patches EmbeddedModelField.validate to allow None values when null=True which is expected behaviour.

    Upstream bug:
        EmbeddedModelField.validate always checks to see if the value is an instance of the EmbeddedModel. Even when
        it's set to be nullable, it will still throw an error when it is null as None is not an instance of Embedded
        model. This patch allows it to correctly return early when null = true and value is none.
    """
    from django_mongodb_backend.fields import EmbeddedModelField

    # avoid double patching
    if hasattr(EmbeddedModelField, "_original_validate"):
        return

    original_validate = EmbeddedModelField.validate

    def patched_validate(self, value, model_instance):
        if value is None:
            models.Field.validate(self, value, model_instance)
            if self.null:
                return
        original_validate(self, value, model_instance)

    EmbeddedModelField.validate = patched_validate

    # this is so we can test the original bug still exists, and if it doesnt we can delete this patch
    EmbeddedModelField._original_validate = original_validate
