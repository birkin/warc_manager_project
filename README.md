# purpose

This webapp will enable the public to:
- search for and view pages.

This webapp will enable staff to:
- Phase one:
    - request collections to be downloaded.
    - view the status of requested downloads.
- Phase two:
    - request `additions` to be downloaded.

---


# Future thoughts

- For future, consider adding a collection-snapshots model to track changes over time.
  This could contain snapshots of archivit data, and snapshots of on-disk data.

---


# Technical note: 

This webapp auto-creates a UserProfile record, automatically, whenever a new User record is created -- whether via code or via the admin. The UserProfile record can contain additional data beyond Django's built-in fixed minimal data-fields. Example use-case: if one wanted to refer to a user by UUID, the UUID field would be added to the UseProfile record.

To enable that:
- models.UserProfile() was created
- apps.py was added to the warc_manager_app -- specifically to load signals.py
- signals.py was added to trigger the UserProfile auto-creation
- settings.py was updated to specify `warc_manager_app.apps.WarcManagerAppConfig`, instead of just `warc_manager_app`

---
