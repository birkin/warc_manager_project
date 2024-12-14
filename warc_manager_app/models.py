import uuid

from django.db import models
from django.conf import settings


class Collection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    collection_id = models.CharField(max_length=50, unique=True)
    item_count = models.IntegerField()
    size_in_bytes = models.BigIntegerField()
    notes = models.TextField()
    status = models.TextChoices('status', 'QUERIED QUEUED_FOR_START QUEUED_FOR_REDO IN_PROGRESS PAUSED COMPLETE')
    all_files = models.JSONField()  # list; will likely eventually become a separate File model
    errors = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def size_in_gigabytes(self) -> float:
        return round(self.size_in_bytes / (1024 ** 3), 2)

    def __str__(self):
        return self.collection_id


class UserProfile(models.Model):
    """
    This extends the User object to include additional fields.

    This webapp is set up to auto-create a UserProfile record when a User record is created.
    See the README for more info about that.
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    can_initiate_downloads = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s profile"
