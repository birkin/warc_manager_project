"""
Implements signals for the bdr_deposits_uploader_app.
Enables auto-creation of a UserProfile record when a new User record is created.
See the README for more info.
"""

import logging

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from warc_manager_app.models import UserProfile

log = logging.getLogger(__name__)


# @receiver(post_save, sender=settings.AUTH_USER_MODEL)
# def create_or_update_user_profile(sender, instance, created, **kwargs):
#     log.debug('starting create_or_update_user_profile()')
#     if created:
#         log.debug('creating a UserProfile record')
#         UserProfile.objects.create(user=instance)
#     else:
#         log.debug('updating a UserProfile record')
#         UserProfile.objects.get_or_create(user=instance)
#         instance.userprofile.save()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    log.debug('starting create_or_update_user_profile()')
    if created:
        log.debug('creating a UserProfile record')
        # Check if a UserProfile already exists to avoid duplication
        UserProfile.objects.get_or_create(user=instance)
    else:
        log.debug('updating a UserProfile record')
        # Update or save an existing UserProfile
        instance.userprofile.save()
