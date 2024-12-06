# purpose

This webapp enables staff to:
- request collections to be downloaded.
- view the status of requested collections

--- 

---

Note that this webapp is configured to auto-create a UserProfile record, automatically, whenever a new User record is created -- whether via code or via the admin.

To enable that:
- models.UserProfile() was created
- apps.py was added to the warc_manager_app -- specifically to load signals.py
- signals.py was added to trigger the UserProfile auto-creation
- settings.py was updated to specify `warc_manager_app.apps.WarcManagerAppConfig`, instead of just `warc_manager_app`
---
