import uuid

from django.conf import settings
from django.db import models


class Collection(models.Model):
    """
    For reference:
    - null=True means the field is allowed to be empty in the database.
    - blank=True means the field is allowed to be empty in forms (including the admin).

    Notes:
    - STATUS_CHOICES contains commented out options that may be used in the future.
    - For future, consider adding a collection-snapshots model to track changes over time.
      This could contain snapshots of archivit data, and snapshots of on-disk data.
    - al_files_on_arc may eventually become a separate Files model.
    """

    STATUS_CHOICES = (  # used by the status field; meaning: (db-code, human-readable description)
        ('queried', 'Queried'),
        ('download_requested', 'Download requested'),
        # ('additions_requested', 'Download additions requested'),
        ('download_in_progress', 'Download in progress'),
        # ('additions_download_in_progress', 'Download-Additions in progress'),
        # ('download_paused', 'Download paused'),
        ('download_complete', 'Download complete'),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    arc_collection_id = models.CharField(
        max_length=50,
        unique=True,
    )
    item_count = models.IntegerField(blank=True)
    size_in_bytes = models.BigIntegerField(blank=True, null=True)
    notes = models.TextField(default='', blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, blank=True, null=True)
    status_history = models.JSONField(default=dict, blank=True)  # list of status changes
    all_files_on_arc = models.JSONField(default=dict, blank=True)
    all_files_on_disc = models.JSONField(default=dict, blank=True)
    errors = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def size_in_gigabytes(self) -> float:
        """
        Allows usage like `collection.size_in_gigabytes` to get the size in GB
        """
        return round(self.size_in_bytes / (1024**3), 2)

    def __str__(self):
        return self.collection_id


class UserProfile(models.Model):
    """
    Extends the User object to include additional fields.

    This webapp is set up to auto-create a UserProfile record when a User record is created.
    See the README for more info about that.
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    can_initiate_downloads = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s profile"
