import uuid

from django.db import models


class Collection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    collection_id = models.CharField(max_length=50, unique=True)
    item_count = models.IntegerField()
    size_in_bytes = models.BigIntegerField()
    notes = models.TextField()
    status = models.TextChoices('status', 'QUERIED QUEUED_FOR_START QUEUED_FOR_REDO IN_PROGRESS PAUSED COMPLETE')
    all_files = models.JSONField()  # list; will likely become a separate File model
    errors = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.collection_id
