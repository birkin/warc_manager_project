"""
Notes...
- I don't usually use an apps.py file.
- My understanding is that it offers a way to run configuration code when the app is first loaded.
- I'm using what appears to be the default configuration -- even though I'm moving away
  from working with integers for my models, in favor of UUIDs.
- The reason I'm adding this file is to try a suggestion for having a UserProfile record auto-created when
  a User record is created.
"""

import logging
import types

from django.apps import AppConfig

log = logging.getLogger(__name__)


class WarcManagerAppConfig(AppConfig):
    log.debug('starting WarcManagerAppConfig')
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'warc_manager_app'

    def ready(self):
        log.debug('starting ready()')
        import warc_manager_app.signals  # this is the reason for this apps.py file

        log.debug(f'type(warc_manager_app.signals): {type(warc_manager_app.signals)}')
        assert type(warc_manager_app.signals) is types.ModuleType
        log.debug('done with ready()')
